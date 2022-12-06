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
from databank import *


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
# Netzanschluss = 20.000 #€/Netzanschluss

OPEX_STORAGE_RATE = 0.02
OPEX_TRAILER_RATE = 0.02

CAPACITY_TUBETRAILER_1 = 378
CAPACITY_TUBETRAILER_2 = 744
CAPACITY_TUBETRAILER_3 = 1100

CAPEX_TRAILER_200bar = 450000
CAPEX_TRAILER_350bar = 550000
CAPEX_TRAILER_550bar = 660000

CAPEX_STORAGE_CH2_EURO_PRO_KG = 500
CAPEX_STORAGE_LH2_EURO_PRO_KG = 40

CAPEX_COMPRESSOR_1 = 71000  # 20-30 auf 100-200 bar
CAPEX_COMPRESSOR_2 = 450000  # bis 550 bar
OPEX_COMPRESSOR_1 = 0.05 * 71000
OPEX_COMPRESSOR_2 = 0.02 * 450000


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

# @dataclasses
# class InfrastructureData:
    # amount_trailer: int
    # storage_dimension: float
    # onsite_storage: float
    # transport_pressure: int
    # pipe_length: float
    # throughput: float
    # throughput_m3: float
    # throughput_kw: float
    # capacity: int
    # energy_demand_year: float


# Function calculates the production profile for a renewable energy plant
def output_power_production(input_technology, power_input, location, share_input_wind, share_input_pv):
    input_technology = str(input_technology)
    power_input = float(power_input)  # MWel
    location = str(location)

    list1 = list(range(0, 8760))
    list1[0:8760] = [int(0) for i in list1[0:8760]]

    list2 = list(range(0, 8760))

    if input_technology == "Wind+PV":  # TODO Einheiten: - * MWel * kwh ???
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

    if math.isclose(power_cost, 0.0):  # power_cost == 0: TODO: Funktion verstehe ich nicht. Die power cost werden doch indiv. eingegeben.
        power_cost1 = pd.DataFrame(get_price_series(power_price_series), columns=['price'])
        power_cost = power_cost1 * price_change
    else:
        list2 = list1.copy()
        list2[0:8760] = [float(power_cost) for i in list2[0:8760]]
        power_cost = pd.DataFrame({"price": list2})

    profit = (output_pp['pv_production'] + output_pp['wind_production']) * power_cost['price']  # hier auf die berechnete power production zugegriffen?

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
            x_production = pd.DataFrame(
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
            x_production = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": re_demand,
                 "grid_demand": list2, "power_production": power_production})

    elif input_technology == "Grid":
        if margincost_model == "yes":
            comparison_margincost1 = np.where(margincost['price'] < product_price, 1, 0)
            comparison_margincost2 = pd.DataFrame({'production': comparison_margincost1})
            x_production3 = pd.DataFrame({'production': (comparison_margincost2['production'] * efficiency * power_technology)})
            grid_demand = x_production3['production'] / efficiency
            x_production = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": list2,
                 "grid_demand": grid_demand, "power_production": list2})

        elif margincost_model == "no":
            list3 = list1.copy()
            list3[0:8760] = [(power_technology * efficiency) for i in list3[0:8760]]
            x_production3 = pd.DataFrame({'production': list3})
            grid_demand = x_production3['production'] / efficiency
            x_production = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": list2,
                 "grid_demand": grid_demand, "power_production": list2})

    elif input_technology == "Wind+Grid" or input_technology == "PV+Grid":
        if margincost_model == "yes":
            comparison_margincost1 = np.where(margincost['price'] < product_price, 1, 0)
            comparison_margincost2 = pd.DataFrame({'production': comparison_margincost1})
            x_production3 = pd.DataFrame({'production': (comparison_margincost2['production'] * efficiency * power_technology)})
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
            x_production = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": re_demand,
                 "grid_demand": grid_demand['grid_demand'], "power_production": power_production['power_production']})
        elif margincost_model == "no":
            list3 = list1.copy()
            list3[0:8760] = [(power_technology * efficiency) for i in list3[0:8760]]
            x_production3 = pd.DataFrame({'production': list3})
            re_demand = output_pp
            grid_demand1 = (x_production3['production'] / efficiency) - re_demand
            grid_demand = pd.DataFrame({'grid_demand': grid_demand1})
            x_production = pd.DataFrame(
                {"time": list1, "production": x_production3['production'], "renewable_demand": re_demand,
                 "grid_demand": grid_demand['grid_demand'],"power_production": list2})

    return x_production


# Function calculates the profitability (NPV and cash flows over runtime) for the designed Power-to-X plant
def dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost, power_price_series,
                   variable_cost, product_price, input_technology, power_input, capex_power, opex_power,
                   efficiency, margincost_model, location, wacc, price_change, regulations_grid_expenditure,
                   EEG_expenditure, capex_decrease, opex_decrease,
                   share_input_wind, share_input_pv):

    if input_technology != "Grid":
        dcf_power = dcf_power_production(input_technology, power_input, capex_power, opex_power, runtime,
                                         location, power_cost, power_price_series,
                                         wacc, price_change, share_input_wind, share_input_pv)[0]

    output_ptx = output_power_to_x(power_technology, input_technology, efficiency, product_price, margincost_model,
                      variable_cost, location, power_input, power_price_series, price_change,
                      share_input_wind, share_input_pv)

    list1 = list(range(0, 8760))
    list1[0:8760] = [int(0) for i in list1[0:8760]]

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

    grid_cost = power_cost['price'] * output_ptx['grid_demand']
    variable_cost1 = variable_cost * output_ptx['production']
    x_production_cost1 = pd.DataFrame({"production_costs": (variable_cost1 + grid_cost)})
    x_production_cost = x_production_cost1['production_costs']
    # According to current research: 40% EGG for own use, 100% for grid purchase.
    variable_regulations_cost_1 = (-0.4) * EEG_expenditure * output_ptx['renewable_demand'].sum()
    variable_regulations_cost_2 = (-1) * (EEG_expenditure + regulations_grid_expenditure) * output_ptx['grid_demand'].sum()

    # Here below: If wind or PV were used, then the costs from wind and PV are added
    if output_ptx["renewable_demand"].sum() > 0:
        power_production_cost = (-1) * dcf_power['expenditure']
    else:
        list1 = list(range(0, runtime + 1))
        power_production_cost = list1.copy()
        power_production_cost = [int(0) for i in power_production_cost]

    list1 = list(range(0, runtime + 1))
    regulations_cost = list1.copy()
    regulations_cost = [(variable_regulations_cost_1 + variable_regulations_cost_2) for i in regulations_cost]
    regulations_cost[0] = 0

    revenue = product_price * output_ptx['production']
    revenue_power = output_ptx['power_production'] * power_cost['price']

    list3 = list(range(0, runtime + 1))

    list4 = list3.copy()
    list4 = [((-1) * opex_plant) for i in list4]
    list4[0] = (-1) * capex_plant

    list5 = list3.copy()
    list5 = [revenue.sum() for i in list5]
    list5[0] = 0

    list6 = list3.copy()
    list6 = [revenue_power.sum() for i in list6]
    list6[0] = 0

    list7 = list3.copy()
    list7 = [(-1) * (x_production_cost.sum()) for i in list7]
    list7[0] = 0

    power_to_x_dcf = pd.DataFrame(
        {"year": list3, "expenditure_technology": list4, "expenditure_power_production": power_production_cost,
         "expenditure_power_grid": list7,
         "expenditure_regulations": regulations_cost, "revenue_technology": list5, "revenue_power": list6})

    power_to_x_dcf['profit'] = power_to_x_dcf['expenditure_technology'] + power_to_x_dcf['expenditure_power_production']\
                               + power_to_x_dcf["expenditure_power_grid"] + power_to_x_dcf['revenue_technology'] + power_to_x_dcf['revenue_power'] \
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
        x_production = pd.DataFrame({"time": list1, "power_production": power_production1, "heat_production": heat_production1,
                                     "input_product_demand": input_product_demand})
    elif margincost_model == "no":
        list2 = list1.copy()
        list2[0:8760] = [float(power_technology) for i in list2[0:8760]]
        input_product_demand = pd.DataFrame({"production": list2})
        power_production = input_product_demand['production'] * efficiency_el
        heat_production = input_product_demand['production'] * efficiency_q
        x_production = pd.DataFrame({"time": list1, "power_production": power_production, "heat_production": heat_production,
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

    xtp_dcf = pd.DataFrame({"year": list3, "expenditure": list4, "feedstock_cost": list5, "revenue_heat": list6, "revenue_power": list7})
    xtp_dcf['profit'] = xtp_dcf['expenditure'] + xtp_dcf['feedstock_cost'] + xtp_dcf['revenue_heat'] + xtp_dcf['revenue_power']

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
                             power_input, power_cost, power_price_series, efficiency_el,
                             efficiency_q, price_change,
                             share_input_wind, share_input_pv, min_storage_dimension_kg, storage_time_hour):

    list_ptx = ["Power-to-X"]
    list_xtp = ["X-to-Power"]

    if ptx_technology in list_ptx:
        output_ptx = output_power_to_x(power_technology, input_technology, efficiency, product_price,
                                       margincost_model, variable_cost, location,
                                       power_input, power_price_series, price_change,
                                       share_input_wind, share_input_pv)
        output1 = output_ptx['production']  # in MWh

    elif ptx_technology in list_xtp:
        output_xtp = output_x_to_power(power_cost, power_technology, product_price, efficiency_el, efficiency_q,
                          margincost_model, variable_cost, price_change)
        output1 = output_xtp["input_product_demand"]  # in MWh

    output = pd.DataFrame({"production": output1})  # in MWh
    output_kw = output['production'] * 1000  # in kWh

    # Umrechnung von kWh in kg der Produktions-Profile
    production_profile1 = output_kw/33.33
    production_profile = pd.DataFrame({"production": production_profile1})

    throughput = production_profile['production'].max()  # maximum throughput is design throughput of compressor

    # maximum throughput is design throughput of compressor und Pipeline Auslegung
    throughput_m3 = throughput/0.09
    throughput_kw = output_kw.max()

    # wir brauchen trotzdem einen Speicher für den produzierten Wasserstoff (On-Site EL)
    if do_infrastructure == 'no':
        if storage_time_hour > 0:
            storage_dimension = throughput * storage_time_hour  # wenn storage_time == 0 -> storage_dimension = 0
        else:
            storage_dimension = 0
        amount_trailer = 0
        onsite_storage = 0
        transport_pressure = 0
        pipe_length = 0
        capacity = 0
        if storage_dimension > 0:
            energy_demand_year = ENERGY_DEMAND_COMPRESSOR * production_profile['production'].sum()  # only if storage_dimension > 0
        else:
            energy_demand_year = 0
    else:
        if infrastructure_type == "Pipeline":
            storage_dimension = 0
            onsite_storage = 0
            amount_trailer = 0
            pipe_length = int(distance)
            transport_pressure = 0
            capacity = 0
            energy_demand_year = 0

        if infrastructure_type == "Tubetrailer":
            amount_trailer = 1
            pipe_length = 0
            loading_time = 1.5
            speed = 50
            transport_time = 2 * (int(distance) / int(speed)) + 2 * (int(loading_time))
            if production_profile['production'].sum() < 36 * CAPACITY_TUBETRAILER_1:
                capacity = CAPACITY_TUBETRAILER_1
                transport_pressure = 200
            elif production_profile['production'].sum() < 36 * CAPACITY_TUBETRAILER_2:
                capacity = CAPACITY_TUBETRAILER_1
                transport_pressure = 350
            elif production_profile['production'].sum() < 36 * CAPACITY_TUBETRAILER_3:
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
            storage_dimension_m3 = storage_dimension / 0.09

            energy_demand_year = ENERGY_DEMAND_COMPRESSOR * production_profile['production'].sum()

        if infrastructure_type == "LNG":
            amount_trailer = 1
            pipe_length = 0
            transport_pressure = 0
            loading_time = 3
            speed = 50
            transport_time = 2 * (int(distance) / int(speed)) + 2 * (int(loading_time))
            capacity = 4300
            amount_tours_year = (production_profile['production'].sum()) / capacity  # Angaben in kg
            interval_tours_hours = (8760 / amount_tours_year) - transport_time  # alle x Stunden kommt eine Lieferung
            interval_tours_days = interval_tours_hours / 24  # alle x tage kommt eine Lieferung
            # Zwischenspeicher am Produktionsort muss die maximale H2-Produktion über das kalkulierte
            # Belieferungsintervall speichern könne
            onsite_storage = interval_tours_days * (throughput * 24)
            onsite_storage_m3 = onsite_storage / 0.09

            storage_dimension = capacity + min_storage_dimension_kg
            storage_dimension_m3 = storage_dimension / 0.09

            energy_demand_year = ENERGY_DEMAND_LIQU * production_profile['production'].sum()

    return (amount_trailer, storage_dimension, onsite_storage, transport_pressure, pipe_length, throughput,
            throughput_m3, throughput_kw, capacity, energy_demand_year)


# Function calculates the costs (NPV and cash flows over runtime) for the designed infrastructure
def infrastructure_dcf(do_infrastructure, infrastructure_type, runtime, wacc, power_cost, infrastructure):

    if do_infrastructure == 'no':
        capex_storage = CAPEX_STORAGE_CH2_EURO_PRO_KG * infrastructure[1]
        opex_storage = OPEX_STORAGE_RATE * capex_storage
        cost_energy_demand_year = infrastructure[9] * power_cost
        capex_compressor = CAPEX_COMPRESSOR_1
        opex_compressor = OPEX_COMPRESSOR_1 + cost_energy_demand_year
        capex_onsite_storage = 0
        opex_onsite_storage = 0
        opex_transport = 0
        capex_liqu = 0
        opex_liqu = 0
        capex_evaporator = 0
        opex_evaporator = 0
        capex_lh2_pump = 0
        opex_lh2_pump = 0
        capex_trailer = 0

    else:
        if infrastructure_type == "Pipeline":
            if infrastructure[6] < GAS_FLOW_HOUR_1:
                capex_pipe = CAPEX_PIPE_1 * infrastructure[4]
            elif infrastructure[6] < GAS_FLOW_HOUR_2:
                capex_pipe = CAPEX_PIPE_2 * infrastructure[4]
            elif infrastructure[6] < GAS_FLOW_HOUR_3:
                capex_pipe = CAPEX_PIPE_3 * infrastructure[4]
            elif infrastructure[6] < GAS_FLOW_HOUR_4:
                capex_pipe = CAPEX_PIPE_4 * infrastructure[4]
            else:
                print("MAX PIPELINE TO SMALL -> USING MAX PIPELINE")
                capex_pipe = CAPEX_PIPE_4 * infrastructure[4]  # TODO: Was, wenn max. Pipeline zu klein
            opex_pipe = OPEX_PIPE_RATE * capex_pipe
            # Druckreduktion in Pipeline für Endanwendung durch GDRMA alle 35 km. (Mind. 2)
            gdrma_amount = max(math.ceil(infrastructure[4] / 35), 2)
            capex_gdrma = gdrma_amount * GDRMA
            opex_transport = opex_pipe
            capex_storage = 0
            opex_storage = 0
            capex_onsite_storage = 0
            opex_onsite_storage = 0
            capex_liqu = 0
            opex_liqu = 0
            capex_evaporator = 0
            opex_evaporator = 0
            capex_lh2_pump = 0
            opex_lh2_pump = 0
            capex_compressor = 0
            opex_compressor = 0
            capex_trailer = 0

        if infrastructure_type == "Tubetrailer":
            capex_onsite_storage = infrastructure[2] * CAPEX_STORAGE_CH2_EURO_PRO_KG
            opex_onsite_storage = capex_onsite_storage * OPEX_STORAGE_RATE
            capex_storage = infrastructure[1] * CAPEX_STORAGE_CH2_EURO_PRO_KG
            opex_storage = OPEX_STORAGE_RATE * capex_storage
            cost_energy_demand_year = infrastructure[9] * power_cost
            if infrastructure[3] == 200:
                capex_compressor = CAPEX_COMPRESSOR_1
                opex_compressor = OPEX_COMPRESSOR_1 + cost_energy_demand_year
                capex_trailer = CAPEX_TRAILER_200bar
            elif infrastructure[3] == 350:
                capex_compressor = CAPEX_COMPRESSOR_1 + CAPEX_COMPRESSOR_2
                opex_compressor = OPEX_COMPRESSOR_1 + OPEX_COMPRESSOR_2 + cost_energy_demand_year
                capex_trailer = CAPEX_TRAILER_350bar
            elif infrastructure[3] == 550:
                capex_compressor = CAPEX_COMPRESSOR_1 + CAPEX_COMPRESSOR_2
                opex_compressor = OPEX_COMPRESSOR_1 + OPEX_COMPRESSOR_2 + cost_energy_demand_year
                capex_trailer = CAPEX_TRAILER_550bar
            opex_trailer = OPEX_TRAILER_RATE * capex_trailer
            opex_transport = opex_trailer + OPEX_TRUCK
            capex_liqu = 0
            opex_liqu = 0
            capex_evaporator = 0
            opex_evaporator = 0
            capex_lh2_pump = 0
            opex_lh2_pump = 0

        if infrastructure_type == "LNG":
            capex_onsite_storage = infrastructure[2] * CAPEX_STORAGE_LH2_EURO_PRO_KG
            opex_onsite_storage = capex_onsite_storage * OPEX_STORAGE_RATE
            capex_storage = infrastructure[1] * CAPEX_STORAGE_LH2_EURO_PRO_KG
            opex_storage = OPEX_STORAGE_RATE * capex_storage
            capex_trailer = infrastructure[0] * 200 * infrastructure[8]  # capex_trailer_spez = 200
            opex_trailer = OPEX_TRAILER_RATE * capex_trailer
            opex_transport = opex_trailer + OPEX_TRUCK
            cost_energy_demand_year = infrastructure[9] * power_cost
            capex_liqu = 105000000 * max((((infrastructure[5] * 24)/50)**0.66), 1)
            opex_liqu = OPEX_LIQU_RATE * capex_liqu + cost_energy_demand_year
            capex_evaporator = CAPEX_EVA_EURO_PRO_KG * (infrastructure[5] * 24)
            opex_evaporator = OPEX_EVA_RATE * capex_evaporator
            capex_lh2_pump = CAPEX_PUMP_EURO_PRO_KG * (infrastructure[5] * 24)
            opex_lh2_pump = OPEX_PUMP_RATE * capex_lh2_pump
            capex_compressor = 0
            opex_compressor = 0

    list3 = list(range(0, runtime + 1))

    list4 = [((-1) * (opex_transport)) for _ in range(len(list3))]
    list4[0] = 0
    if do_infrastructure == "yes":
        if infrastructure_type == "Pipeline":
            for i in range(len(list4)):
                if i % AMORTIZATION_PIPE == 0:
                    list4[i] -= capex_pipe
                if i % AMORTIZATION_GDRMA == 0:
                    list4[i] -= capex_gdrma
        else:
            for i in range(len(list4)):
                if i % AMORTIZATION_TRUCK == 0:
                    list4[i] -= CAPEX_TRUCK
                if i % AMORTIZATION_TRAILER == 0:
                    list4[i] -= capex_trailer
    # hier soll rein, dass nach X Jahren Komponenten ausgetauscht werden müssen und entsprechend die CaPex nach X Jahren
    # erneut anfallen
    # Jährliche Energiekosten solln in einer Spalte angezeigt werden oder zu den Kosten in Liste 5 addiert werden

    list5 = [((-1) * (opex_compressor + opex_liqu + opex_evaporator + opex_lh2_pump)) for _ in range(len(list3))]
    list5[0] = 0
    if do_infrastructure == "yes":
        if infrastructure_type == "Tubetrailer":
            for i in range(len(list5)):
                if i % AMORTIZATION_COMPRESSOR == 0:
                    list5[i] -= capex_compressor
        if infrastructure_type == "LNG":
            for i in range(len(list5)):
                if i % AMORTIZATION_LIQU == 0:
                    list5[i] -= capex_liqu
                if i % AMORTIZATION_EVA == 0:
                    list5[i] -= capex_evaporator
                if i % AMORTIZATION_PUMP == 0:
                    list5[i] -= capex_lh2_pump
        if infrastructure_type == "Pipeline":
            list5[0] = 0
    # do_infrastructure == "no":
    else:
        for i in range(len(list5)):
            if i % AMORTIZATION_COMPRESSOR == 0:
                list5[i] -= capex_compressor

    list6 = [((-1) * (opex_storage + opex_onsite_storage)) for _ in range(len(list3))]
    list6[0] = 0
    if do_infrastructure == "yes":
        if infrastructure_type == "Pipeline":
            list6[0] = 0
        else:
            for i in range(len(list6)):
                if i % AMORTIZATION_STORAGE == 0:
                    list6[i] -= capex_storage
                if i % AMORTIZATION_ONSITE_STORAGE == 0:
                    list6[i] -= capex_onsite_storage
    else:
        for i in range(len(list6)):
            if i % AMORTIZATION_STORAGE == 0:
                list6[i] -= capex_storage
            if i % AMORTIZATION_ONSITE_STORAGE == 0:
                list6[i] -= capex_onsite_storage

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


def sensitivity(power_technology, capex_technology, opex_technology, runtime, power_cost, power_price_series,
                variable_cost, product_price, input_technology, power_input, capex_power, opex_power,
                efficiency, margincost_model, location, wacc, price_change, regulations_grid_expenditure,
                EEG_expenditure, capex_decrease, opex_decrease,
                share_input_wind, share_input_pv):
    output = {"capex_technology": [], "opex_technology": [], "capex_power": [], "opex_power": [], "efficiency": [],
              "wacc": []}
    for x in range(20):
        factor = (x/10)
        _, npv = dcf_power_to_x(power_technology, capex_technology * factor, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, input_technology, power_input,
                                capex_power, opex_power, efficiency, margincost_model, location, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                share_input_wind, share_input_pv)
        output["capex_technology"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology * factor, runtime, power_cost,
                                power_price_series, variable_cost, product_price, input_technology, power_input,
                                capex_power, opex_power, efficiency, margincost_model, location, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                share_input_wind, share_input_pv)
        output["opex_technology"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, input_technology, power_input,
                                capex_power * factor, opex_power, efficiency, margincost_model, location, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                share_input_wind, share_input_pv)
        output["capex_power"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, input_technology, power_input,
                                capex_power, opex_power * factor, efficiency, margincost_model, location, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                share_input_wind, share_input_pv)
        output["opex_power"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, input_technology, power_input,
                                capex_power, opex_power, efficiency * factor, margincost_model, location, wacc, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                share_input_wind, share_input_pv)
        output["efficiency"].append(npv)
        _, npv = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                                power_price_series, variable_cost, product_price, input_technology, power_input,
                                capex_power, opex_power, efficiency, margincost_model, location, wacc * factor, price_change,
                                regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                                share_input_wind, share_input_pv)
        output["wacc"].append(npv)
    for name, values in output.items():
        plt.plot(values, label=name)
    plt.ylabel('Net Present Value [€]')
    plt.xlabel('Change')
    plt.legend()
    plt.savefig("static/sensitivity_plot.png")
    plt.figure(1)
    plt.close()

