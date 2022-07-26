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
from databank import *



# Function calculates the production profile for a renewable energy plant
def output_power_production(input_technology, power_input, location, share_input_wind, share_input_pv):
    input_technology = str(input_technology)
    power_input = float(power_input)
    location = str(location)

    list1 = list(range(0, 8760))
    list1[0:8760] = [int(0) for i in list1[0:8760]]

    list2 = list(range(0, 8760))

    if input_technology == "Wind+PV":
        production_pv = share_input_pv * power_input * \
                        pd.DataFrame(dict_ort[location][0], columns=['electricity'])
        production_wind = share_input_wind * power_input * \
                          pd.DataFrame(dict_ort[location][1], columns=['electricity'])

    elif input_technology == "PV" or input_technology == "PV+Grid":
        production_pv = power_input * pd.DataFrame(dict_ort[location][0], columns=['electricity'])
        production_wind = power_input * pd.DataFrame(list1, columns=['electricity'])
    elif input_technology == "Wind" or input_technology == "Wind+Grid":
        production_wind = power_input * pd.DataFrame(dict_ort[location][1], columns=['electricity'])
        production_pv = power_input * pd.DataFrame(list1, columns=['electricity'])

    power_production = pd.DataFrame({"time":list2, "pv_production": production_pv['electricity'], "wind_production": production_wind['electricity']})

    return (power_production)


# Function calculates the profitability (NPV and cash flows over runtime) for the designed RE plant
def dcf_power_production(input_technology, power_input, capex_power, opex_power,
                         runtime, location, power_cost, wacc, price_change,
                         share_input_wind, share_input_pv):
    list1 = list(range(0, 8760))
    list1[0:8760] = [int(0) for i in list1[0:8760]]

    capex_plant = int(capex_power) * int(power_input)
    opex_plant = int(opex_power) * int(power_input)

    output_pp = output_power_production(input_technology, power_input, location, share_input_wind, share_input_pv)


    if math.isclose(power_cost, 0.0):#power_cost == 0:
        power_cost1 = pd.DataFrame(electricity_cost_data, columns=['price'])
        power_cost = power_cost1 * price_change
    else:
        list2 = list1.copy()
        list2[0:8760] = [int(power_cost) for i in list2[0:8760]]
        power_cost = pd.DataFrame({"price": list2})

    profit = (output_pp['pv_production'] + output_pp['wind_production']) * power_cost['price']

    list1 = list(range(1, runtime + 1))

    list2 = list1.copy()
    list2[0] = opex_plant + capex_plant
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

    return (power_production_dcf,npv)



# Function calculates the production profile for a Power-to-X plant
def output_power_to_x(power_technology, input_technology, efficiency, product_price,
                      margincost_model, variable_cost, location, power_input, price_change,
                      share_input_wind, share_input_pv):
    list1 = list(range(0, 8760))
    list2 = list1.copy()
    list2[0:8760] = [int(0) for i in list2[0:8760]]
    margincost1 = pd.DataFrame(electricity_cost_data, columns=['price'])
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
           #here below and also in the other functions it is described that either the produced amount from RE is the
           #limit, or the installed capacity of the plant. So if the RE production is greater than the installed power
           #of the plant, then the power is chosen as the limit of the production (cf. max_power2) Otherwise the RE
           #quantity is the limiting quantity (cf. max_power1).
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

    return (x_production)


# Function calculates the profitability (NPV and cash flows over runtime) for the designed Power-to-X plant
def dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime, power_cost,
                   variable_cost, product_price, input_technology, power_input, capex_power, opex_power,
                   efficiency, margincost_model, location, wacc, price_change, regulations_grid_expenditure,
                   EEG_expenditure, capex_decrease, opex_decrease,
                   share_input_wind, share_input_pv):

    if input_technology != "Grid":
        dcf_power = dcf_power_production(input_technology, power_input, capex_power, opex_power, runtime,
                                location, power_cost, wacc, price_change, share_input_wind, share_input_pv)[0]

    output_ptx = output_power_to_x(power_technology, input_technology, efficiency, product_price, margincost_model,
                      variable_cost, location, power_input, price_change,
                      share_input_wind, share_input_pv)

    list1 = list(range(0, 8760))
    list1[0:8760] = [int(0) for i in list1[0:8760]]

    capex_plant = int(capex_technology) * int(power_technology) * float(capex_decrease)
    opex_plant = int(opex_technology) * int(power_technology) * float(opex_decrease)
    runtime = int(runtime)
    list2 = list1.copy()
    list2[0:8760] = [int(power_cost) for i in list2[0:8760]]

    if math.isclose(power_cost, 0.0):#power_cost is int(0):
        power_cost1 = pd.DataFrame(electricity_cost_data, columns=['price'])
        power_cost = power_cost1 * price_change
    else:
        list2 = list1.copy()
        list2[0:8760] = [int(power_cost) for i in list2[0:8760]]
        power_cost = pd.DataFrame({"price": list2})

    grid_cost = power_cost['price'] * output_ptx['grid_demand']
    variable_cost1 = variable_cost * output_ptx['production']
    x_production_cost1 = pd.DataFrame({"production_costs": (variable_cost1 + grid_cost)})
    x_production_cost = x_production_cost1['production_costs']
    #According to current research: 40% EGG for own use, 100% for grid purchase.
    variable_regulations_cost_1 = (-0.4) * EEG_expenditure * output_ptx['renewable_demand'].sum()
    variable_regulations_cost_2 = (-1) * (EEG_expenditure + regulations_grid_expenditure) * output_ptx['grid_demand'].sum()

    #Here below: If wind or PV were used, then the costs from wind and PV are added
    if output_ptx["renewable_demand"].sum() > 0:
        power_production_cost = (-1) * dcf_power['expenditure']
    else:
        list1 = list(range(1, runtime + 1))
        power_production_cost = list1.copy()
        power_production_cost = [int(0) for i in power_production_cost]

    list1 = list(range(1, runtime + 1))
    regulations_cost = list1.copy()
    regulations_cost = [(variable_regulations_cost_1 + variable_regulations_cost_2) for i in regulations_cost]

    revenue = product_price * output_ptx['production']
    revenue_power = output_ptx['power_production'] * power_cost['price']

    list3 = list(range(1, runtime + 1))

    list4 = list3.copy()
    list4[0] = (-1) * (opex_plant + capex_plant + x_production_cost.sum())
    list4[1:-1] = [((-1) * (opex_plant + x_production_cost.sum())) for i in list4[1:-1]]
    list4[-1] = (-1) * (opex_plant + x_production_cost.sum())

    list5 = list3.copy()
    list5 = [revenue.sum() for i in list5]

    list6 = list3.copy()
    list6 = [revenue_power.sum() for i in list6]


    power_to_x_dcf = pd.DataFrame(
        {"year": list3, "expenditure_technology": list4, "expenditure_power_production": power_production_cost,
         "expenditure_regulations": regulations_cost, "revenue_technology": list5, "revenue_power": list6})

    power_to_x_dcf['profit'] = power_to_x_dcf['expenditure_technology'] + power_to_x_dcf['expenditure_power_production']\
                               + power_to_x_dcf['revenue_technology'] + power_to_x_dcf['revenue_power'] \
                               + power_to_x_dcf["expenditure_regulations"]

    x = 0
    list3 = list(range(0,runtime))
    npv_calc = list3
    ptx_profit = power_to_x_dcf['profit']
    while x < int(runtime):
        npv_calc[x] = ptx_profit[x] / (1 + wacc) ** int(x)
        x += 1

    npv = sum(npv_calc)

    return (power_to_x_dcf,npv)



#Function calculates the production profile for a X-to-Power plant
def output_x_to_power(power_cost, power_technology, product_price, efficiency_el, efficiency_q, margincost_model,
                      variable_cost, price_change):
    list1 = list(range(0, 8760))

    if math.isclose(power_cost, 0.0):#power_cost == 0:
        marginrevenue1 = pd.DataFrame(electricity_cost_data, columns=['price'])
        marginrevenue = marginrevenue1 * price_change
    else:
        list2 = list1.copy()
        list2 = [power_cost for i in list2]
        marginrevenue = pd.DataFrame({"price": list2})

    margincost = product_price / efficiency_el + variable_cost

    if margincost_model == "yes":
        comparison_margincost1 = np.where(marginrevenue['price'] > margincost, 1, 0)
        comparison_margincost = pd.DataFrame({'production': comparison_margincost1})
        power_production1 = comparison_margincost['production'] * power_technology * efficiency_el
        heat_production1 = comparison_margincost['production'] * power_technology * efficiency_q
        input_product_demand = comparison_margincost['production'] * power_technology
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

    return (x_production)



#Function calculates the profitability (NPV and cash flows over runtime) for the designed X-to-Power plant
def dcf_x_to_power(power_technology, capex_technology, opex_technology, runtime, product_price,
                   variable_cost, power_cost, heat_cost, efficiency_el, efficiency_q, margincost_model, wacc,
                   price_change, capex_decrease, opex_decrease):

    output_xtp = output_x_to_power(power_cost, power_technology, product_price, efficiency_el, efficiency_q, margincost_model,
                      variable_cost, price_change)

    list1 = list(range(0, 8760))

    capex_plant = int(capex_technology) * int(power_technology) * capex_decrease
    opex_plant = int(opex_technology) * int(power_technology) * opex_decrease
    runtime = int(runtime)
    list2 = list1.copy()
    list2[0:8760] = [int(power_cost) for i in list2[0:8760]]

    if math.isclose(power_cost, 0.0):#power_cost is int(0):
        power_cost3 = pd.DataFrame(electricity_cost_data, columns=['price'])
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

    list3 = list(range(1, runtime + 1))

    list4 = list3.copy()
    list4[0] = (-1) * (opex_plant + capex_plant)
    list4[1:-1] = [((-1) * opex_plant) for i in list4[1:-1]]
    list4[-1] = ((-1) * opex_plant)

    list5 = list3.copy()
    list5 = [((-1) * x_production_cost.sum()) for i in list5]

    list6 = list3.copy()
    list6 = [heat_revenue.sum() for i in list6]

    list7 = list3.copy()
    list7 = [power_revenue.sum() for i in list7]

    xtp_dcf = pd.DataFrame({"year": list3, "expenditure": list4, "feedstock_cost": list5, "revenue_heat": list6, "revenue_power": list7})
    xtp_dcf['profit'] = xtp_dcf['expenditure'] + xtp_dcf['feedstock_cost'] + xtp_dcf['revenue_heat'] + xtp_dcf['revenue_power']

    x = 0
    npv_calc = list3
    xtp_profit = xtp_dcf['profit']
    while x < int(runtime):
        npv_calc[x] = xtp_profit[x] / ((1 + wacc)**int(x))
        x += 1
    npv = sum(npv_calc)

    return (xtp_dcf,npv)



#Function calculates the technical dimension for infrastructure
def infrastructure_dimension(ptx_technology, infrastructure_type, distance, power_technology, input_technology,
                             efficiency, product_price, margincost_model, variable_cost, location, power_input,
                             power_cost, efficiency_el, efficiency_q, price_change, transport_pressure, capacity,
                             share_input_wind, share_input_pv):

    list_ptx = ["Power-to-X"]
    list_xtp = ["X-to-Power"]

    if ptx_technology in list_ptx:
        output_ptx = output_power_to_x(power_technology, input_technology, efficiency, product_price,
                                       margincost_model, variable_cost, location, power_input, price_change,
                                       share_input_wind, share_input_pv)
        output1 = output_ptx['production']

    elif ptx_technology in list_xtp:
        output_xtp = output_x_to_power(power_cost, power_technology, product_price, efficiency_el, efficiency_q,
                          margincost_model, variable_cost, price_change)
        output1 = output_xtp["input_product_demand"]

    output = pd.DataFrame({"production": output1})

    # Umrechnung von MWh in kg der Produktions-Profile
    production_profile1 = output['production'] * (1000/33.33)
    production_profile = pd.DataFrame({"production": production_profile1})

    throughput = production_profile['production'].max()  #maximum throughput is design throughput of compressor

    if infrastructure_type == "Pipeline":
        gas_flow_hour = (throughput * 259.8 * 273) / (
                    transport_pressure * (10 ^ 5))  #volume flow with ideal gas law
        gas_flow = gas_flow_hour / (60 * 60)
        pipe_diameter = math.sqrt((4 / math.pi) * (gas_flow / (20 / 3.6)))
        #formula for calculation of the pipe diameter (20/3.6 entspricht 20 kmh in m/s)

        storage_dimension = 0
        amount_storage = 0
        amount_trailer = 0
        pipe_length = int(distance)

    else:
        pipe_diameter = 0
        pipe_length = 0
        loading_time = 2
        speed = 50
        timeframe = 16

        transportdauer = int(distance) / int(speed) + int(loading_time)
        daily_tours = timeframe / transportdauer
        daily_production = (production_profile['production'].sum()) / 365
        amount_tours_day = daily_production / capacity
        amount_trailer = math.ceil(amount_tours_day / daily_tours)

        storage_dimension = (timeframe / amount_tours_day) * production_profile['production'].max()
        amount_storage = math.ceil(storage_dimension / 400)
        #every x hours is transported away, resulting in a storage requirement of "x * fullload-production"
        #assumption: One storage container can store 400 kg

    return (amount_trailer, storage_dimension, amount_storage, transport_pressure,
            pipe_diameter, pipe_length, throughput)


# Function calculates the costs (NPV and cash flows over runtime) for the designed infrastructure
def infrastructure_dcf(ptx_technology, infrastructure_type, distance, power_technology, input_technology,
                       efficiency, product_price, margincost_model, variable_cost, location, power_input,
                       power_cost, efficiency_el, efficiency_q, runtime, wacc, price_change, capex_compressor_1,
                       capex_compressor_2, opex_compressor_rate, capex_pipe_1, capex_pipe_2,
                       capex_pipe_3, opex_pipe_rate, capex_trailer, capex_storagetank, transport_pressure,
                       capacity, opex_trailer, capex_liquifier, opex_liquifier_rate, share_input_wind, share_input_pv):

    infrastructure = infrastructure_dimension(ptx_technology, infrastructure_type, distance, power_technology,
                                              input_technology, efficiency, product_price, margincost_model,
                                              variable_cost, location, power_input, power_cost, efficiency_el,
                                              efficiency_q, price_change, transport_pressure, capacity,
                                              share_input_wind, share_input_pv)


    if infrastructure[2] > 0:
        capex_storage = infrastructure[2] * capex_storagetank
        opex_storage = 0.02 * capex_storage
    else:
        capex_storage = 0
        opex_storage = 0

    if infrastructure[0] > 0:
        capex_transport = infrastructure[0] * capex_trailer
        opex_transport = opex_trailer

    elif infrastructure[4] > 0:
        if 0.25 > infrastructure[4] > 0:
            capex_transport = capex_pipe_1 * infrastructure[5]
        elif 0.5 > infrastructure[4] > 0.25:
            capex_transport = capex_pipe_2 * infrastructure[5]
        elif infrastructure[4] > 0.5:
            capex_transport = capex_pipe_3 * infrastructure[5]

        opex_transport = opex_pipe_rate * capex_transport

    #calcualtion of compressor cost
    if infrastructure[3] == 20:
        capex_compressor = capex_compressor_1 * power_technology
        opex_compressor = opex_compressor_rate * capex_compressor
        capex_liqu = 0
        opex_liqu = 0
    elif infrastructure[3] == 400:
        capex_compressor = capex_compressor_2 * power_technology
        opex_compressor = opex_compressor_rate * capex_compressor
        capex_liqu = 0
        opex_liqu = 0
    if infrastructure_type == "LNG":
        capex_liqu = capex_liquifier * infrastructure[6]
        opex_liqu = opex_liquifier_rate * capex_liqu
        capex_compressor = 0
        opex_compressor = 0

    list3 = list(range(1, runtime + 1))

    list4 = list3.copy()
    list4[0] = (-1) * (opex_transport + capex_transport)
    list4[1:-1] = [((-1) * (opex_transport)) for i in list4[1:-1]]
    list4[-1] = (-1) * (opex_transport)

    list5 = list3.copy()
    list5[0] = (-1) * (opex_compressor + capex_compressor + opex_liqu + capex_liqu)
    list5[1:-1] = [((-1) * (opex_compressor + opex_liqu)) for i in list5[1:-1]]
    list5[-1] = (-1) * (opex_compressor + opex_liqu)

    list6 = list3.copy()
    list6[0] = (-1) * (opex_storage + capex_storage)
    list6[1:-1] = [((-1) * (opex_storage)) for i in list6[1:-1]]
    list6[-1] = (-1) * (opex_storage)

    infrastructure_dcf = pd.DataFrame({"year": list3, "expenditure_transport": list4,
                                       "expenditure_compressor": list5, "expenditure_storage": list6})
    infrastructure_dcf['expenditure_total'] = infrastructure_dcf["expenditure_transport"] \
                                              + infrastructure_dcf["expenditure_compressor"] \
                                              + infrastructure_dcf["expenditure_storage"]
    x = 0
    npv_calc = list3
    infr_profit = infrastructure_dcf['expenditure_total']
    while x < int(runtime):
        npv_calc[x] = infr_profit[x] / ((1 + wacc)**int(x))
        x += 1
    npv = sum(npv_calc)

    return (infrastructure_dcf, npv)
