'''
This is OBMETSC, the Open-source Business Model Evaluation Tool
for Sector Coupling technologies. Developed at the chair
of Energy and Recource Management at the Technische
Universität Berlin.
---------------------------------------
Functions File:
The functions include the mathematical calculation
logic for determining the production and profitability
SPDX-FileCopyrightText: Arian Hohgraeve <a.e.hohgraeve@web.de>
SPDX-FileCopyrightText: Johannes Giehl
SPDX-License-Identifier: MIT
'''


import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import PercentFormatter
import copy
from dataclasses import dataclass
from databank import *
from typing import List


#gas_flow_hour in m3/h für die unterschiedlichen Pipelines im VNB
GAS_FLOW_HOUR_1 = 49.89
GAS_FLOW_HOUR_2 = 81.73
GAS_FLOW_HOUR_3 = 801.49
GAS_FLOW_HOUR_4 = 3205.94


CAPEX_PIPE_1 = 400000  # in €/km (DN25/DP1)
CAPEX_PIPE_2 = 400000  # (DN32/DP1)
CAPEX_PIPE_3 = 850000  # (DN100/DP4)
CAPEX_PIPE_4 = 950000  # (DN200/DP4)
OPEX_PIPE_RATE = 0.04
GDRMA = 77000  # €/Stück, eine Anlage alle 35 km, 400 m3/h
GDRMA_2 = 132000  # €/Stück, eine Anlage alle 35 km, 1000 m3/h
# Netzanschluss = 20.000 #€/Netzanschluss

CAPACITY_TUBETRAILER_1 = 378
CAPACITY_TUBETRAILER_2 = 744
CAPACITY_TUBETRAILER_3 = 1100
OPEX_TRAILER_RATE = 0.02

CAPEX_TRAILER_200bar = 170000  # 460 * 378 = 173.880€ (100 bar) Sens; 150.000€ (162 bar und 300 kg) Y&O
CAPEX_TRAILER_350bar = 520000  # 720 * 744 = 535.680€ (250 bar) US DOC 2015
CAPEX_TRAILER_550bar = 670000  # sens: 680.000 (500 bar, 1100 kg); US DOC 2015: 600 €/kg (500 bar, 1100 kg), 660.000 reuß 2019

# CAPEX_STORAGE_CH2_EURO_PRO_KG = 500
CAPEX_STORAGE_CH2_EURO_PRO_M3 = 1500
CAPEX_STORAGE_LH2_EURO_PRO_KG = 40
OPEX_STORAGE_RATE = 0.02

CAPEX_COMPRESSOR_1 = 71000  # 20-30 auf 100-200 bar
CAPEX_COMPRESSOR_2 = 450000  # bis 550 bar
OPEX_COMPRESSOR_1 = 0.04 * 71000
OPEX_COMPRESSOR_2 = 0.02 * 450000

CAPEX_TRAILER_LH2 = 200  # €/kg

OPEX_LIQU_RATE = 0.04
CAPEX_EVA_EURO_PRO_KG = 3000  # Euro pro kg pro Tag
OPEX_EVA_RATE = 0.03
CAPEX_PUMP_EURO_PRO_KG = 30000  # Euro pro kg pro Tag
OPEX_PUMP_RATE = 0.03

CAPEX_TRUCK = 175000
OPEX_TRUCK = 0.12 * 175000

AMORTIZATION_TRUCK = 8
AMORTIZATION_TRAILER = 20
AMORTIZATION_STORAGE = 30
AMORTIZATION_ONSITE_STORAGE = 30
AMORTIZATION_COMPRESSOR = 15
AMORTIZATION_LIQU = 20
AMORTIZATION_EVA = 10
AMORTIZATION_PUMP = 10
AMORTIZATION_PIPE = 40
AMORTIZATION_GDRMA = 45

ENERGY_DEMAND_COMPRESSOR = 1  # kWh el pro kg H2
ENERGY_DEMAND_LIQU = 7
ENERGY_DEMAND_EVA = 0
ENERGY_DEMAND_PUMP = 0

@dataclass
class InfrastructureData:
    storage_dimension: float
    storage_dimension_m3: float
    onsite_storage: float
    transport_pressure: int
    pipe_length: float
    throughput: float
    throughput_m3: float
    throughput_kw: float
    capacity: int
    energy_demand_year: float
    transport_time: float
    amount_tours_year: int

@dataclass
class XProductionData:
    time: List[int]
    production: List[float]
    renewable_demand: List[float]
    grid_demand: List[float]
    power_production: List[float]


# Function calculates the production profile for a renewable energy plant
def output_power_production(input_technology, power_input, location, share_input_wind, share_input_pv):
    input_technology = str(input_technology)
    power_input = float(power_input)  # MWel
    location = str(location)

    list1 = list(range(0, 8760))
    list1[0:8760] = [int(0) for i in list1[0:8760]]

    list2 = list(range(0, 8760))

    if input_technology == "Wind+PV":
        production_pv = share_input_pv * power_input * \
                        (pd.DataFrame(dict_ort[location][0], columns=['electricity']))
        production_wind = share_input_wind * power_input * \
                        (pd.DataFrame(dict_ort[location][1], columns=['electricity']))

    elif input_technology == "PV" or input_technology == "PV+Grid":
        production_pv = power_input * (pd.DataFrame(dict_ort[location][0], columns=['electricity']))
        production_wind = power_input * pd.DataFrame(list1, columns=['electricity'])  # alle Werte in der Liste 0
    elif input_technology == "Wind" or input_technology == "Wind+Grid":
        production_wind = power_input * (pd.DataFrame(dict_ort[location][1], columns=['electricity']))
        production_pv = power_input * pd.DataFrame(list1, columns=['electricity'])  # alle Werte in der Liste sind 0
    # input_technology == "Grid"
    # else:
        # production_wind = 0
        # production_pv = 0

    power_production = pd.DataFrame({"time": list2, "pv_production": production_pv['electricity'],
                                     "wind_production": production_wind['electricity']})

    return power_production



# Function calculates the profitability (NPV and cash flows over runtime) for the designed RE plant
def dcf_power_production(input_technology, power_input, capex_power, opex_power,
                         runtime, location, power_cost, power_price_series, wacc, price_change,
                         share_input_wind, share_input_pv):
    list1 = list(range(0, 8760))
    list1[0:8760] = [int(0) for i in list1[0:8760]]

    capex_plant = float(capex_power) * float(power_input)
    opex_plant = float(opex_power) * float(power_input)

    output_pp = output_power_production(input_technology, power_input, location, share_input_wind, share_input_pv)

    if math.isclose(power_cost, 0.0):
        power_cost1 = pd.DataFrame(get_price_series(power_price_series), columns=['price'])
        power_cost = power_cost1 * price_change
    else:
        list2 = list1.copy()
        list2[0:8760] = [float(power_cost) for i in list2[0:8760]]
        power_cost = pd.DataFrame({"price": list2})

    profit = (output_pp['pv_production'] + output_pp['wind_production']) * power_cost['price']

    list1 = list(range(0, runtime + 1))

    list2 = list1.copy()
    list2[0] = capex_plant
    list2[1:-1] = [opex_plant for i in list2[1:-1]]
    list2[-1] = opex_plant

    list3 = list1.copy()
    list3 = [profit.sum() for i in list3]

    power_production_dcf = pd.DataFrame({"year": list1, "expenditure": list2, "revenue": list3})
    power_production_dcf["profit"] = power_production_dcf["revenue"] - power_production_dcf["expenditure"]

    x = 0
    npv_calc = list3
    pp_profit = power_production_dcf['profit']
    while x < int(runtime):
        npv_calc[x] = pp_profit[x] / ((1 + wacc)**int(x))
        x += 1
    npv = sum(npv_calc)

    return power_production_dcf, npv


# Function calculates the production profile for a Power-to-X plant
def output_power_to_x(power_technology, input_technology, efficiency, product_price,
                      margincost_model, variable_cost, location, power_input,
                      power_price_series, price_change,
                      share_input_wind, share_input_pv):
    list1 = list(range(0, 8760))
    list2 = list1.copy()
    list2[0:8760] = [int(0) for i in list2[0:8760]]
    margincost1 = pd.DataFrame(get_price_series(power_price_series), columns=['price'])
    margincost = (margincost1 * price_change) / efficiency + variable_cost

    if input_technology != "Grid":
        output_pv = output_power_production(input_technology, power_input, location,
                                            share_input_wind, share_input_pv)['pv_production']
        output_wind = output_power_production(input_technology, power_input, location,
                                              share_input_wind, share_input_pv)['wind_production']
        output_pp = output_pv + output_wind

    if input_technology == "Wind" or input_technology == "PV" or input_technology == "Wind+PV":
        if margincost_model == "yes":
            comparison_margincost1 = np.where(margincost['price'] < product_price, 1, 0)
            comparison_margincost2 = pd.DataFrame({'production': comparison_margincost1})
            # here below and also in the other functions it is described that either the produced amount from RE is the
            # limit, or the installed capacity of the plant. So if the RE production is greater than the installed power
            # of the plant, then the power is chosen as the limit of the production (cf. max_power2) Otherwise the RE
            # quantity is the limiting quantity (cf. max_power1).
            max_power1 = np.where(output_pp <= power_technology, 1, 0)
            max_power2 = np.where(output_pp <= power_technology, 0, power_technology)
            max_power3 = pd.DataFrame({'production': max_power1})
            max_power4 = pd.DataFrame({'production': max_power2})
            x_production1 = comparison_margincost2['production'] * output_pp * efficiency * max_power3['production']
            x_production2 = comparison_margincost2['production'] * efficiency * max_power4['production']
            x_production3 = pd.DataFrame({"production": x_production1 + x_production2})
            re_demand = x_production3['production'] / efficiency
            power_production = output_pp - re_demand
            output_ptx = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": re_demand,
                 "grid_demand": list2, "power_production": power_production})
        elif margincost_model == "no":
            max_power1 = np.where(output_pp <= power_technology, 1, 0)
            max_power2 = np.where(output_pp <= power_technology, 0, power_technology)
            max_power3 = pd.DataFrame({'production': max_power1})
            max_power4 = pd.DataFrame({'production': max_power2})
            x_production1 = output_pp * efficiency * max_power3['production']
            x_production2 = efficiency * max_power4['production']
            x_production3 = pd.DataFrame({"production": x_production1 + x_production2})
            re_demand = x_production3['production'] / efficiency
            power_production = output_pp - re_demand
            output_ptx = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": re_demand,
                 "grid_demand": list2, "power_production": power_production})

    elif input_technology == "Grid":
        if margincost_model == "yes":
            comparison_margincost1 = np.where(margincost['price'] < product_price, 1, 0)
            comparison_margincost2 = pd.DataFrame({'production': comparison_margincost1})
            x_production3 = pd.DataFrame({'production': (comparison_margincost2['production'] * efficiency *
                                                         power_technology)})
            grid_demand = x_production3['production'] / efficiency
            output_ptx = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": list2,
                 "grid_demand": grid_demand, "power_production": list2})

        elif margincost_model == "no":
            list3 = list1.copy()
            list3[0:8760] = [(power_technology * efficiency) for i in list3[0:8760]]
            x_production3 = pd.DataFrame({'production': list3})
            grid_demand = x_production3['production'] / efficiency
            output_ptx  = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": list2,
                 "grid_demand": grid_demand, "power_production": list2})

    elif input_technology == "Wind+Grid" or input_technology == "PV+Grid":
        if margincost_model == "yes":
            comparison_margincost1 = np.where(margincost['price'] < product_price, 1, 0)
            comparison_margincost2 = pd.DataFrame({'production': comparison_margincost1})
            x_production3 = pd.DataFrame({'production': (comparison_margincost2['production'] * efficiency *
                                                         power_technology)})
            max_power_plant1 = np.where(output_pp <= power_technology, 1, 0)
            max_power_plant2 = np.where(output_pp <= power_technology, 0, power_technology)
            max_power_plant3 = pd.DataFrame({'production': max_power_plant1})
            max_power_plant4 = pd.DataFrame({'production': max_power_plant2})
            plant_demand1 = comparison_margincost2['production'] * output_pp * max_power_plant3[
                'production']
            plant_demand2 = comparison_margincost2['production'] * max_power_plant4['production']
            re_demand = plant_demand1 + plant_demand2
            power_production1 = output_pp - re_demand
            power_production = pd.DataFrame({'power_production': power_production1})
            grid_demand1 = (x_production3['production'] / efficiency) - re_demand
            grid_demand = pd.DataFrame({'grid_demand': grid_demand1})
            output_ptx = XProductionData(time=list1, production=x_production3['production'],
                                         renewable_demand=re_demand,
                                         grid_demand=grid_demand['grid_demand'],
                                         power_production=power_production['power_production'])
        elif margincost_model == "no":
            list3 = list1.copy()
            list3[0:8760] = [(power_technology * efficiency) for i in list3[0:8760]]
            x_production3 = pd.DataFrame({'production': list3})
            re_demand = output_pp
            grid_demand1 = (x_production3['production'] / efficiency) - re_demand
            grid_demand = pd.DataFrame({'grid_demand': grid_demand1})
            output_ptx = XProductionData(time=list1, production=x_production3['production'], renewable_demand=re_demand,
                                         grid_demand=grid_demand['grid_demand'], power_production=list2)

    return output_ptx


def LCOH2(runtime, wacc, plant_production, dcf_expenditure_technology, dcf_expenditure_power_production,
                               dcf_expenditure_power_grid, dcf_expenditure_regulations):

    # calculate the annuity factor for given runtime and wacc
    annuity_factor = (((1+wacc)**runtime)-1) / (((1+wacc)**runtime)*wacc)

    # calculate the investment cost and discoutned annual cost based on the reduces dcf dataframe
    total_investment = dcf_expenditure_technology.loc[0] + dcf_expenditure_power_production.loc[0] + \
                       dcf_expenditure_power_grid.loc[0] + dcf_expenditure_regulations.loc[0]

    annual_cost = (dcf_expenditure_technology.loc[1] + dcf_expenditure_power_production.loc[1] +
                   dcf_expenditure_power_grid.loc[1] + dcf_expenditure_regulations.loc[1]) * annuity_factor
    total_discounted_cost = (total_investment + annual_cost) * -1

    # calculate the discounted production based on the plant productin profil
    discounted_production = plant_production * annuity_factor

    # claculate the levelised cost
    Levelized_cost = total_discounted_cost / discounted_production

    return Levelized_cost


# Function calculates the profitability (NPV and cash flows over runtime) for the designed Power-to-X plant
def dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost, power_price_series,
                   variable_cost, product_price, wacc, price_change, regulations_grid_expenditure,
                   EEG_expenditure, capex_decrease, opex_decrease, output_ptx, dcf_power_expenditure):

    list1 = list(range(0, 8760))
    list1[0:8760] = [int(0) for i in list1[0:8760]]
    variable_cost1 = sum(output_ptx.production) * variable_cost
    capex_plant = float(capex_technology) * float(power_technology) * float(capex_decrease)
    opex_plant = float(opex_technology) * float(power_technology) * float(opex_decrease)
    runtime = int(runtime)
    list2 = list1.copy()
    list2[0:8760] = [float(power_cost) for i in list2[0:8760]]

    if math.isclose(power_cost, 0.0):  # power_cost is int(0):
        power_cost1 = pd.DataFrame(get_price_series(power_price_series), columns=['price'])
        power_cost = power_cost1 * price_change
    else:
        list2 = list1.copy()
        list2[0:8760] = [float(power_cost) for i in list2[0:8760]]
        power_cost = pd.DataFrame({"price": list2})

    grid_cost = power_cost['price'] * output_ptx.grid_demand
    x_production_cost1 = pd.DataFrame({"production_costs": grid_cost})
    x_production_cost = x_production_cost1['production_costs']
    # According to current research: 40% EGG for own use, 100% for grid purchase.
    variable_regulations_cost_1 = (-0.4) * EEG_expenditure * sum(output_ptx.renewable_demand)
    variable_regulations_cost_2 = (-1) * (EEG_expenditure + regulations_grid_expenditure) * sum(output_ptx.grid_demand)

    # Here below: If wind or PV were used, then the costs from wind and PV are added
    if sum(output_ptx.renewable_demand) > 0:
        power_production_cost = (-1) * dcf_power_expenditure
    else:
        list1 = list(range(0, runtime + 1))
        power_production_cost = list1.copy()
        power_production_cost = [int(0) for i in power_production_cost]

    list1 = list(range(0, runtime + 1))
    regulations_cost = list1.copy()
    regulations_cost = [(variable_regulations_cost_1 + variable_regulations_cost_2) for i in regulations_cost]
    regulations_cost[0] = 0

    revenue = product_price * sum(output_ptx.production)
    revenue_power = output_ptx.power_production * power_cost['price']

    list3 = list(range(0, runtime + 1))

    list4 = list3.copy()
    list4 = [(-1) * (opex_plant + variable_cost1) for i in list4]
    list4[0] = (-1) * capex_plant

    list5 = list3.copy()
    list5 = [revenue for i in list5]
    list5[0] = 0

    list6 = list3.copy()
    list6 = [revenue_power.sum() for i in list6]
    list6[0] = 0

    list7 = list3.copy()
    list7 = [-1 * (x_production_cost.sum()) for i in list7]
    list7[0] = 0

    power_to_x_dcf = pd.DataFrame(
        {"year": list3, "expenditure_technology": list4, "expenditure_power_production": power_production_cost,
         "expenditure_power_grid": list7,
         "expenditure_regulations": regulations_cost, "revenue_technology": list5, "revenue_power": list6})

    power_to_x_dcf['profit'] = power_to_x_dcf['expenditure_technology'] + \
                               power_to_x_dcf['expenditure_power_production']\
                               + power_to_x_dcf["expenditure_power_grid"] + power_to_x_dcf['revenue_technology'] + \
                               power_to_x_dcf['revenue_power'] \
                               + power_to_x_dcf["expenditure_regulations"]

    x = 0
    list3 = list(range(0, runtime+1))
    npv_calc = list3
    ptx_profit = power_to_x_dcf['profit']
    while x < int(runtime+1):
        npv_calc[x] = ptx_profit[x] / (1 + wacc) ** int(x)
        x += 1

    npv = sum(npv_calc)

    return power_to_x_dcf, npv


# Function calculates the production profile for a X-to-Power plant
def output_x_to_power(power_cost, power_price_series, power_technology,
                      product_price, efficiency_el, efficiency_q, margincost_model,
                      variable_cost, price_change):
    list1 = list(range(0, 8760))

    if math.isclose(power_cost, 0.0):  # power_cost == 0:
        marginrevenue1 = pd.DataFrame(get_price_series(power_price_series), columns=['price'])
        marginrevenue = marginrevenue1 * price_change
    else:
        list2 = list1.copy()
        list2 = [power_cost for i in list2]
        marginrevenue = pd.DataFrame({"price": list2})

    margincost = product_price / efficiency_el + variable_cost

    if margincost_model == "yes":
        comparison_margincost1 = np.where(marginrevenue['price'] > margincost, 1, 0)
        comparison_margincost = pd.DataFrame({'production': comparison_margincost1})
        power_production1 = comparison_margincost['production'] * power_technology  # * efficiency_el
        heat_production1 = comparison_margincost['production'] * power_technology * efficiency_q
        input_product_demand = comparison_margincost['production'] * power_technology / efficiency_el
        x_production = pd.DataFrame({"time": list1, "power_production": power_production1,
                                     "heat_production": heat_production1, "input_product_demand": input_product_demand})
    elif margincost_model == "no":
        list2 = list1.copy()
        list2[0:8760] = [float(power_technology) for i in list2[0:8760]]
        input_product_demand = pd.DataFrame({"production": list2})
        power_production = input_product_demand['production'] * efficiency_el
        heat_production = input_product_demand['production'] * efficiency_q
        x_production = pd.DataFrame({"time": list1, "power_production": power_production,
                                     "heat_production": heat_production,
                                     "input_product_demand": input_product_demand['production']})

    return x_production


# Function calculates the profitability (NPV and cash flows over runtime) for the designed X-to-Power plant
def dcf_x_to_power(power_technology, capex_technology, opex_technology, runtime, product_price,
                   variable_cost, power_cost, power_price_series,
                   heat_cost, efficiency_el, efficiency_q, margincost_model, wacc,
                   price_change, capex_decrease, opex_decrease):

    output_xtp = output_x_to_power(power_cost, power_price_series, power_technology,
                                   product_price, efficiency_el, efficiency_q, margincost_model,
                                   variable_cost, price_change)

    list1 = list(range(0, 8760))

    capex_plant = int(capex_technology) * int(power_technology) * capex_decrease
    opex_plant = int(opex_technology) * int(power_technology) * opex_decrease
    runtime = int(runtime)
    list2 = list1.copy()
    list2[0:8760] = [int(power_cost) for i in list2[0:8760]]

    if math.isclose(power_cost, 0.0):  # power_cost is int(0):
        power_cost3 = pd.DataFrame(get_price_series(power_price_series), columns=['price'])
        power_cost2 = power_cost3 * price_change
    else:
        list2 = list1.copy()
        list2[0:8760] = [int(power_cost) for i in list2[0:8760]]
        power_cost2 = pd.DataFrame({"price": list2})

    if heat_cost is int(0):
        heat_cost2 = pd.DataFrame(heat_cost_data, columns=['price'])
    else:
        list2 = list1.copy()
        list2[0:8760] = [heat_cost for i in list2[0:8760]]
        heat_cost2 = pd.DataFrame({"price": list2})

    feedstock_cost = product_price * output_xtp['input_product_demand']
    variable_cost1 = variable_cost * output_xtp['power_production']
    x_production_cost1 = pd.DataFrame({"production_costs": (variable_cost1 + feedstock_cost)})
    x_production_cost = x_production_cost1['production_costs']

    power_revenue = output_xtp['power_production'] * power_cost2['price']
    heat_revenue = output_xtp['heat_production'] * heat_cost2['price']

    list3 = list(range(0, runtime + 1))

    list4 = list3.copy()
    list4[0] = (-1) * (0 + capex_plant)
    list4[1:-1] = [((-1) * opex_plant) for i in list4[1:-1]]
    list4[-1] = ((-1) * opex_plant)

    list5 = list3.copy()
    list5 = [((-1) * x_production_cost.sum()) for i in list5]
    list5[0] = 0

    list6 = list3.copy()
    list6 = [heat_revenue.sum() for i in list6]
    list6[0] = 0

    list7 = list3.copy()
    list7 = [power_revenue.sum() for i in list7]
    list7[0] = 0

    xtp_dcf = pd.DataFrame({"year": list3, "expenditure": list4, "feedstock_cost": list5, "revenue_heat": list6,
                            "revenue_power": list7})
    xtp_dcf['profit'] = xtp_dcf['expenditure'] + xtp_dcf['feedstock_cost'] + xtp_dcf['revenue_heat'] + \
                        xtp_dcf['revenue_power']

    x = 0
    npv_calc = list3
    xtp_profit = xtp_dcf['profit']
    while x < int(runtime+1):
        npv_calc[x] = xtp_profit[x] / ((1 + wacc)**int(x))
        x += 1
    npv = sum(npv_calc)

    return xtp_dcf, npv


# Function calculates the technical dimension for infrastructure
def infrastructure_dimension(ptx_technology, do_infrastructure, infrastructure_type, distance, power_technology,
                             input_technology, efficiency, product_price, margincost_model, variable_cost, location,
                             power_input, power_cost, power_price_series, efficiency_el, efficiency_q, price_change,
                             share_input_wind, share_input_pv, min_storage_dimension_kg):

    list_ptx = ["Power-to-X"]
    list_xtp = ["X-to-Power"]

    if ptx_technology in list_ptx:
        output_ptx = output_power_to_x(power_technology, input_technology, efficiency, product_price,
                                       margincost_model, variable_cost, location,
                                       power_input, power_price_series, price_change,
                                       share_input_wind, share_input_pv)
        output1 = output_ptx.production  # in MWh

    elif ptx_technology in list_xtp:
        output_xtp = output_x_to_power(power_cost, power_technology, product_price, efficiency_el, efficiency_q,
                          margincost_model, variable_cost, price_change)
        output1 = output_xtp["input_product_demand"]  # in MWh

    output = pd.DataFrame({"production": output1})  # in MWh
    output_kw = output.production * 1000  # in kWh

    # Umrechnung von kWh in kg der Produktions-Profile
    production_profile1 = output_kw/33.33
    production_profile = pd.DataFrame({"production": production_profile1})  # in kg

    throughput = production_profile1.max()  # maximum throughput in kg is design throughput of compressor

    # maximum throughput is design throughput of compressor und Pipeline Auslegung
    throughput_m3 = throughput/0.09
    throughput_kw = output_kw.max()

    # wir brauchen trotzdem einen Speicher für den produzierten Wasserstoff (On-Site EL)
    if do_infrastructure == 'no':
        if min_storage_dimension_kg > 0:
            storage_dimension = min_storage_dimension_kg
        else:
            storage_dimension = 0
        onsite_storage = 0
        transport_pressure = 0
        pipe_length = 0
        capacity = 0
        if storage_dimension > 0:
            energy_demand_year = ENERGY_DEMAND_COMPRESSOR * production_profile['production'].sum()  # only if storage_dimension > 0
        else:
            energy_demand_year = 0
        transport_time = 0
        amount_tours_year = 0

    else:
        if infrastructure_type == "Pipeline":
            storage_dimension = 0
            storage_dimension_m3 = 0
            onsite_storage = 0
            pipe_length = float(distance)
            transport_pressure = 0
            capacity = 0
            energy_demand_year = 0
            transport_time = 0
            amount_tours_year = 0

        if infrastructure_type == "Tubetrailer":
            pipe_length = 0
            loading_time = 1.5
            speed = 50
            transport_time = 2 * (float(distance) / float(speed)) + 2 * (float(loading_time))
            if production_profile['production'].sum() < 52 * CAPACITY_TUBETRAILER_1:
                capacity = CAPACITY_TUBETRAILER_1
                transport_pressure = 200
            elif production_profile['production'].sum() < 53 * CAPACITY_TUBETRAILER_2:
                capacity = CAPACITY_TUBETRAILER_1
                transport_pressure = 350
            elif production_profile['production'].sum() < 53 * CAPACITY_TUBETRAILER_3:
                capacity = CAPACITY_TUBETRAILER_3
                transport_pressure = 550
            else:
                print("MAX CAPACITY REACHED -> AMOUNT OF YEARLY TOURS IS EXCEEDED")
                capacity = CAPACITY_TUBETRAILER_3
                transport_pressure = 550
            amount_tours_year = (production_profile['production'].sum())/capacity  # Angaben in kg
            interval_tours_hours = (8760/amount_tours_year) - transport_time  # alle x Stunden kommt eine Lieferung
            interval_tours_days = interval_tours_hours/24  # alle x Tage kommt eine Lieferung
            # Zwischenspeicher am Produktionsort muss die maximale H2-Produktion über das kalkulierte
            # Belieferungsintervall speichern könne
            onsite_storage = interval_tours_days * (throughput * 24)
            onsite_storage_m3 = onsite_storage / 0.09

            storage_dimension = capacity + min_storage_dimension_kg
            storage_dimension_m3 = storage_dimension / 14

            energy_demand_year = ENERGY_DEMAND_COMPRESSOR * production_profile['production'].sum()

        if infrastructure_type == "LNG":
            pipe_length = 0
            transport_pressure = 0
            loading_time = 3
            speed = 50
            transport_time = 2 * (float(distance) / float(speed)) + 2 * (float(loading_time))
            capacity = 4300
            amount_tours_year = (production_profile['production'].sum()) / capacity  # Angaben in kg
            interval_tours_hours = (8760 / amount_tours_year) - transport_time  # alle x Stunden kommt eine Lieferung
            interval_tours_days = interval_tours_hours / 24  # alle x tage kommt eine Lieferung
            # Zwischenspeicher am Produktionsort muss die maximale H2-Produktion über das kalkulierte
            # Belieferungsintervall speichern könne
            onsite_storage = interval_tours_days * (throughput * 24)
            onsite_storage_m3 = onsite_storage
            storage_dimension = capacity + min_storage_dimension_kg
            storage_dimension_m3 = storage_dimension / 70.99

            energy_demand_year = ENERGY_DEMAND_LIQU * production_profile['production'].sum()

    return InfrastructureData(storage_dimension, storage_dimension_m3, onsite_storage, transport_pressure, pipe_length,
                              throughput, throughput_m3, throughput_kw, capacity, energy_demand_year, transport_time,
                              amount_tours_year)


# Function calculates the costs (NPV and cash flows over runtime) for the designed infrastructure
def dcf_infrastructure(do_infrastructure, infrastructure_type, runtime, wacc, power_cost, distance, infrastructure):
    power_cost_kwh = power_cost / 1000  # von €/MWh zu €/kWh

    if do_infrastructure == 'no':
        storage_dimension_m3 = infrastructure.storage_dimension / 14  # 14 kg/m3 bei 200 bar
        capex_storage = CAPEX_STORAGE_CH2_EURO_PRO_M3 * storage_dimension_m3
        opex_storage = OPEX_STORAGE_RATE * capex_storage
        cost_energy_demand_year = infrastructure.energy_demand_year * power_cost_kwh
        if infrastructure.storage_dimension > 0:
            capex_compressor = CAPEX_COMPRESSOR_1
            opex_compressor = OPEX_COMPRESSOR_1 + cost_energy_demand_year
        else:
            capex_compressor = 0
            opex_compressor = 0
        capex_onsite_storage = 0
        opex_onsite_storage = 0
        opex_transport = 0
        opex_liqu = 0
        opex_evaporator = 0
        opex_lh2_pump = 0
        capex_conversion = capex_compressor
        capex_transport = 0
        driver_cost = 0
        fuel_cost = 0

    else:
        if infrastructure_type == "Pipeline":
            if infrastructure.throughput_m3 < GAS_FLOW_HOUR_1:
                capex_pipe = CAPEX_PIPE_1 * infrastructure.pipe_length
            elif infrastructure.throughput_m3 < GAS_FLOW_HOUR_2:
                capex_pipe = CAPEX_PIPE_2 * infrastructure.pipe_length
            elif infrastructure.throughput_m3 < GAS_FLOW_HOUR_3:
                capex_pipe = CAPEX_PIPE_3 * infrastructure.pipe_length
            elif infrastructure.throughput_m3 < GAS_FLOW_HOUR_4:
                capex_pipe = CAPEX_PIPE_4 * infrastructure.pipe_length
            else:
                print("MAX PIPELINE TO SMALL -> USING MAX PIPELINE")
                capex_pipe = CAPEX_PIPE_4 * infrastructure.pipe_length  # TODO: Was, wenn max. Pipeline zu klein
            opex_pipe = OPEX_PIPE_RATE * capex_pipe
            # Druckreduktion in Pipeline für Endanwendung durch GDRMA alle 35 km. (Mind. 2)
            gdrma_amount = max(math.ceil(infrastructure.pipe_length / 35), 2)
            if infrastructure.throughput_m3 > 400:
                capex_gdrma = gdrma_amount * GDRMA
            else:
                capex_gdrma = gdrma_amount * GDRMA_2
            opex_transport = opex_pipe
            capex_storage = 0
            opex_storage = 0
            capex_onsite_storage = 0
            opex_onsite_storage = 0
            opex_liqu = 0
            opex_evaporator = 0
            opex_lh2_pump = 0
            capex_compressor = 0
            opex_compressor = 0
            capex_trailer = 0
            capex_transport = capex_pipe
            capex_conversion = capex_gdrma
            driver_cost = 0
            fuel_cost = 0

        if infrastructure_type == "Tubetrailer":
            # onsite_storage_m3 = infrastructure.onsite_storage / 14
            # capex_onsite_storage = onsite_storage_m3 * CAPEX_STORAGE_CH2_EURO_PRO_M3
            # opex_onsite_storage = capex_onsite_storage * OPEX_STORAGE_RATE
            # capex_storage = infrastructure.storage_dimension * CAPEX_STORAGE_CH2_EURO_PRO_KG
            storage_dimension_m3 = infrastructure.storage_dimension / 14
            capex_storage = storage_dimension_m3 * CAPEX_STORAGE_CH2_EURO_PRO_M3
            opex_storage = OPEX_STORAGE_RATE * capex_storage
            cost_energy_demand_year = infrastructure.energy_demand_year * power_cost_kwh
            if infrastructure.transport_pressure == 200:
                capex_compressor = CAPEX_COMPRESSOR_1
                opex_compressor = OPEX_COMPRESSOR_1 + cost_energy_demand_year
                capex_trailer = CAPEX_TRAILER_200bar
            elif infrastructure.transport_pressure == 350:
                capex_compressor = 2 * CAPEX_COMPRESSOR_1
                opex_compressor = OPEX_COMPRESSOR_1 + OPEX_COMPRESSOR_2 + cost_energy_demand_year
                capex_trailer = CAPEX_TRAILER_350bar
            elif infrastructure.transport_pressure == 550:
                capex_compressor = CAPEX_COMPRESSOR_1 + CAPEX_COMPRESSOR_2
                opex_compressor = OPEX_COMPRESSOR_1 + OPEX_COMPRESSOR_2 + cost_energy_demand_year
                capex_trailer = CAPEX_TRAILER_550bar
            opex_trailer = OPEX_TRAILER_RATE * capex_trailer
            opex_transport = opex_trailer + OPEX_TRUCK
            capex_transport = capex_trailer + CAPEX_TRUCK
            opex_liqu = 0
            opex_evaporator = 0
            opex_lh2_pump = 0
            capex_conversion = capex_compressor
            driver_cost = (infrastructure.transport_time * 35) * infrastructure.amount_tours_year
            fuel_cost = ((distance/100) * 34.5 * 2) * infrastructure.amount_tours_year

        if infrastructure_type == "LNG":
            # capex_onsite_storage = infrastructure.onsite_storage * CAPEX_STORAGE_LH2_EURO_PRO_KG
            # opex_onsite_storage = capex_onsite_storage * OPEX_STORAGE_RATE
            capex_storage = infrastructure.storage_dimension * CAPEX_STORAGE_LH2_EURO_PRO_KG
            opex_storage = OPEX_STORAGE_RATE * capex_storage
            capex_trailer = CAPEX_TRAILER_LH2 * infrastructure.capacity
            opex_trailer = OPEX_TRAILER_RATE * capex_trailer
            opex_transport = opex_trailer + OPEX_TRUCK
            capex_transport = capex_trailer + CAPEX_TRUCK
            cost_energy_demand_year = infrastructure.energy_demand_year * power_cost_kwh
            capex_liqu = 105000000 * max((((infrastructure.throughput * 24)/50)**0.66), 1)
            opex_liqu = OPEX_LIQU_RATE * capex_liqu + cost_energy_demand_year
            capex_evaporator = CAPEX_EVA_EURO_PRO_KG * (infrastructure.throughput * 24)
            opex_evaporator = OPEX_EVA_RATE * capex_evaporator
            capex_lh2_pump = CAPEX_PUMP_EURO_PRO_KG * (infrastructure.throughput * 24)
            opex_lh2_pump = OPEX_PUMP_RATE * capex_lh2_pump
            opex_compressor = 0
            capex_conversion = capex_lh2_pump + capex_evaporator + capex_liqu
            driver_cost = (infrastructure.transport_time * 35) * infrastructure.amount_tours_year
            fuel_cost = ((distance/100) * 34.5 * 2) * infrastructure.amount_tours_year

    list3 = list(range(0, runtime + 1))
    list4 = [((-1) * (opex_transport + driver_cost + fuel_cost)) for i in range(len(list3))]
    list4[0] = (-1) * capex_transport
    # hier soll rein, dass nach X Jahren Komponenten ausgetauscht werden müssen und entsprechend die CaPex nach X Jahren
    # erneut anfallen
    # Jährliche Energiekosten solln in einer Spalte angezeigt werden oder zu den Kosten in Liste 5 addiert werden

    list5 = [((-1) * (opex_compressor + opex_liqu + opex_evaporator + opex_lh2_pump)) for _ in range(len(list3))]
    list5[0] = (-1) * capex_conversion

    list6 = [((-1) * opex_storage) for _ in range(len(list3))]
    list6[0] = (-1) * capex_storage

    infrastructure_dcf = pd.DataFrame({"year": list3, "expenditure_transport": list4,
                                       "expenditure_conversion": list5, "expenditure_storage": list6})
    infrastructure_dcf['expenditure_total'] = infrastructure_dcf["expenditure_transport"] \
                                              + infrastructure_dcf["expenditure_conversion"] \
                                              + infrastructure_dcf["expenditure_storage"]
    x = 0
    npv_calc = list3
    infr_profit = infrastructure_dcf['expenditure_total']
    while x < int(runtime+1):
        npv_calc[x] = infr_profit[x] / ((1 + wacc)**int(x))
        x += 1
    npv = sum(npv_calc)

    return infrastructure_dcf, npv


def LCOI(runtime, wacc, plant_production, dcf_expenditure_transport, dcf_expenditure_conversion, dcf_expenditure_storage):
    # calculate the annuity factor for given runtime and wacc
    if wacc == 0:
        wacc = 0.01
    annuity_factor = (((1 + wacc) ** runtime) - 1) / (((1 + wacc) ** runtime) * wacc)

    # calculate the investment cost and discoutned annual cost based on the reduces dcf dataframe
    total_investment = dcf_expenditure_transport.loc[0] + dcf_expenditure_conversion.loc[0] + dcf_expenditure_storage.loc[0]

    annual_cost = (dcf_expenditure_transport.loc[1] + dcf_expenditure_conversion.loc[1] +
                   dcf_expenditure_storage.loc[1]) * annuity_factor
    total_discounted_cost = (total_investment + annual_cost) * -1

    # calculate the discounted production based on the plant productin profile
    discounted_production = plant_production * annuity_factor

    # claculate the levelised cost
    Levelized_cost_infra = total_discounted_cost / discounted_production

    return Levelized_cost_infra


def sensitivity(power_technology, capex_technology, opex_technology, runtime, power_cost, power_price_series,
                variable_cost, product_price, wacc, price_change, regulations_grid_expenditure,
                EEG_expenditure, capex_decrease, opex_decrease, output_ptx, dcf_power_expenditure):
    output = {"CapEx (PtX)": [], "Installierte Leistung (PtX)": [], "Strombezugspreis": [], "Variable Kosten": [],
              "Preis für PtX-Energieträger": [], "Zinssatz": [], "OpEx (PtX)": [], "Netzentgelte": [],
              "Jährliche Stromproduktionskosten": [], "Strompreisänderung": [], "Produktionsmenge": []}
    for x in range(20):
        factor = (x/10)
        _, npv = dcf_power_to_x(power_technology, capex_technology * factor, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["CapEx (PtX)"].append(npv)
        _, npv = dcf_power_to_x(power_technology * factor, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["Installierte Leistung (PtX)"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost * factor,
                                power_price_series, variable_cost, product_price, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["Strombezugspreis"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost * factor, product_price, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["Variable Kosten"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price * factor, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["Preis für PtX-Energieträger"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, wacc * factor, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["Zinssatz"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology * factor, runtime, power_cost,
                                power_price_series, variable_cost, product_price, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["OpEx (PtX)"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, wacc, price_change,
                                regulations_grid_expenditure * factor, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["Netzentgelte"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure * factor)
        output["Jährliche Stromproduktionskosten"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, wacc, price_change*factor,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                output_ptx, dcf_power_expenditure)
        output["Strompreisänderung"].append(npv)
        temp = copy.deepcopy(output_ptx)
        temp.production = [x*factor for x in temp.production]
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                temp, dcf_power_expenditure)
        output["Produktionsmenge"].append(npv)
    plt.figure(figsize=(12, 10), dpi=80)
    for name, values in output.items():
       plt.plot(values, label=name)
    plt.xticks(np.arange(0,21,2.5),['0%','25%','50%','75%','100%','125%','150%','175%','200%'], fontsize=12)
    plt.yticks(fontsize=12)
    plt.ylabel('Kapitalwert [€]', fontsize=15)
    plt.xlabel('Parameteranpassung', fontsize=15)
    plt.rcParams.update({'font.size': 15})
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.2, box.width, box.height * 0.9])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=3)
    plt.savefig("static/sensitivity_plot.png")
    plt.close()
    return output


def sensitivity_LCOI(runtime, wacc, plant_production, dcf_expenditure_transport, dcf_expenditure_conversion, dcf_expenditure_storage):
    output_1 = {"Transportkosten": [], "Umwandlungskosten": [], "Speicherkosten": []}
    for x in range(20):
        factor = (x/10)
        levelized_cost_infra = LCOI(runtime, wacc, plant_production, dcf_expenditure_transport*factor,
                                    dcf_expenditure_conversion, dcf_expenditure_storage)
        output_1["Transportkosten"].append(levelized_cost_infra)
        levelized_cost_infra = LCOI(runtime, wacc, plant_production, dcf_expenditure_transport,
                                    dcf_expenditure_conversion*factor, dcf_expenditure_storage)
        output_1["Umwandlungskosten"].append(levelized_cost_infra)
        levelized_cost_infra = LCOI(runtime, wacc, plant_production, dcf_expenditure_transport,
                                    dcf_expenditure_conversion, dcf_expenditure_storage*factor)
        output_1["Speicherkosten"].append(levelized_cost_infra)
    plt.figure(2)
    for name, values in output_1.items():
        plt.plot(values, label=name)
    plt.xticks(np.arange(0, 21, 2.5), ['0%', '25%', '50%', '75%', '100%', '125%', '150%', '175%', '200%'])
    plt.ylabel('Infrastrukturkosten [€/MWh]')
    plt.xlabel('Parameteranpassung')
    plt.legend()
    plt.savefig("static/sensitivity_lcoi_plot.png")
    plt.close()
    return output_1


def sens_LCOH2(runtime, wacc, plant_production, dcf_expenditure_technology, dcf_expenditure_power_production,
               dcf_expenditure_power_grid, dcf_expenditure_regulations):
    output_1 = {"Strombezugskosten - Netz": [], "Ausgaben-Regularien": [], "Elektrolysekosten": [],
                "Stromproduktionskosten - EE": []}
    for x in range(20):
        factor = (x / 10)
        levelized_cost = LCOH2(runtime, wacc, plant_production, dcf_expenditure_technology,
                               dcf_expenditure_power_production,
                               dcf_expenditure_power_grid * factor, dcf_expenditure_regulations)
        output_1["Strombezugskosten - Netz"].append(levelized_cost)
        levelized_cost = LCOH2(runtime, wacc, plant_production, dcf_expenditure_technology,
                               dcf_expenditure_power_production,
                               dcf_expenditure_power_grid, dcf_expenditure_regulations * factor)
        output_1["Ausgaben-Regularien"].append(levelized_cost)
        levelized_cost = LCOH2(runtime, wacc, plant_production, dcf_expenditure_technology * factor,
                               dcf_expenditure_power_production,
                               dcf_expenditure_power_grid, dcf_expenditure_regulations)
        output_1["Elektrolysekosten"].append(levelized_cost)
        levelized_cost = LCOH2(runtime, wacc, plant_production, dcf_expenditure_technology,
                               dcf_expenditure_power_production* factor,
                               dcf_expenditure_power_grid, dcf_expenditure_regulations)
        output_1["Stromproduktionskosten - EE"].append(levelized_cost)
    plt.figure(3)
    for name, values in output_1.items():
        plt.plot(values, label=name)
    plt.xticks(np.arange(0, 21, 2.5), ['0%', '25%', '50%', '75%', '100%', '125%', '150%', '175%', '200%'])
    plt.ylabel('Wasserstoffgestehungskosten [€/MWh]')
    plt.xlabel('Kostenanpassung')
    plt.legend()
    plt.savefig("static/sensitivity_lcox_plot.png")
    plt.close()
    return output_1

