# -*- coding: utf-8 -*-
"""
General description
-------------------
This is OBMETSC, the Open-source Business Model Evaluation Tool
for Sector Coupling technologies. Developed at the chair
of Energy and Recource Management at the Technische
Universität Berlin.

The source code is freely available under MIT license.
Usage of the model is highly encouraged. Contributing is welcome as well.
Repository, Documentation, Installation
---------------------------------------
All founds are hosted on
`GitHub <https://github.com/ADD PATH>`_
To install, simply type ``pip install OBMETSC``
#can we get a pip install?
Please find the documentation `here <ADD LINK>`_
Licensing information and Disclaimer
------------------------------------
This software is provided under MIT License (see licensing file).
A special thank you goes out to all the developers creating,
maintaining, and expanding packages used in this model.
In addition to that, a special thank you goes to all students
and student assistants which have contributed to the model itself
or its data inputs.
Input Data
----------
Input data is provided by the integrated database.
However, most of the data can be set by the user
when running the web application.
Installation requirements
-------------------------
See `environments.yml` file

@author: Arian Hohgräve (*), Johannes Giehl (*)
Contributors:
Joachim Müller-Kirchenbauer
(*) Corresponding authors
"""


import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from functions import *
from flask import Flask, render_template, request

# the lists are necessary to make if-else-actions depending on the technology
list_ptx = ["Power-to-X"] # Power-to-X technologies
list_xtp = ["X-to-Power"] # X-to-Power technologies
list_pp = ["PV", "Wind", "PV+Grid", "Wind+Grid", "Wind+PV"] # input-technologies, based on renewable power production

# creats the webapp with a secret key
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisisasecret'


# the app.route starts an index page which welcomes the user (compare: index.html)
@app.route('/')
def index():
    return render_template("index.html")


# the database page can be selected and gives back the background informations about the tool
@app.route('/database')
def database():
    return render_template("database.html")


# app route that leads user to the tool input page
@app.route('/calculator', methods=['GET', 'POST'])
def input():
    return render_template("input.html")


# this app route shows the results of the tool and appears when you have submit the input
@app.route('/output', methods=['GET', 'POST'])
def get():

    # the following variables are getting the informations from the input.html page
    # demand_h2 = float(request.form['h2_demand']) Angabe auf input.html page in kWh/a
    ptx_technology = str(request.form['ptx_technology'])
    capex_technology = float(request.form['capex_technology'])
    opex_technology = float(request.form['opex_technology'])
    variable_cost = float(request.form['variable_cost'])
    efficiency_ele = float(request.form['efficiency_ele'])
    efficiency_th = float(request.form['efficiency_th'])
    power_technology = float(request.form['power_technology'])
    capex_input = float(request.form['capex_input'])
    opex_input = float(request.form['opex_input'])
    power_cost = float(request.form['power_cost'])
    power_price_series = str(request.form['pp_series'])
    heat_cost = float(request.form['heat_cost'])
    margincost_model = str(request.form['margincost_model'])
    input_technology = str(request.form['input_technology'])
    power_input = float(request.form['power_input'])
    share_input_wind = float(request.form['share_input_wind'])
    share_input_pv = float(request.form['share_input_pv'])
    location = str(request.form['location'])
    power_price_change = float(request.form['power_price_change'])
    infrastructure_type = str(request.form['infrastructure_type'])
    distance = float(request.form['distance'])
    EEG_reduction = float(request.form['EEG_reduction'])
    stromsteuer_reduction = float(request.form['stromsteuer_reduction'])
    KWKG_reduction = float(request.form['KWKG_reduction'])
    netzentgelte_reduction = float(request.form['netzentgelte_reduction'])
    capex_subvention = float(request.form['capex_subvention'])
    opex_subvention = float(request.form['opex_subvention'])
    wacc_input = float(request.form['wacc_input'])
    product_price = float(request.form['product_price'])
    runtime = int(request.form['runtime'])
    do_infrastructure = str(request.form['do_infrastructure'])
    do_storage = str(request.form['do_storage'])
    min_storage_dimension_kwh = float(request.form['storage_dimension'])
    storage_time = float(request.form['storage_dimension'])

    # changes the input date in the needed form for calculation (e.g.: 5% --> 0.05)
    wacc = (wacc_input / 100)  # turning the input wacc (e.g. 5%) into decimal number (e.g. 0.05)
    price_change = 1 + power_price_change / 100  # turning input price_change (e.g. 5%) into decimal number (e.g. 1.05)
    EEG_expenditure = EEG_reduction  # price for MWh power, reduced with input
    stromsteuer_expenditure = stromsteuer_reduction
    KWKG_expenditure = KWKG_reduction
    netzentgelte_expenditure = netzentgelte_reduction  # sum of expenditure from StromNEV, Offshore, Abschaltbare Anlagen, Konzession
    regulations_grid_expenditure = stromsteuer_expenditure + KWKG_expenditure + netzentgelte_expenditure
    capex_decrease = float(1 - (capex_subvention / 100))
    opex_decrease = float(1 - (opex_subvention / 100))
    share_input_wind = float(share_input_wind / 100)
    share_input_pv = float(share_input_pv / 100)
    min_storage_dimension_kg = min_storage_dimension_kwh / 33.3

    # the values are translated into the variables for the functions, efficiency is set as electrical efficiency
    capex_power_kw = capex_input
    opex_power_kw = float(opex_input/100)
    capex_technology_kw = capex_technology
    opex_technology_kw = float(opex_technology/100)
    efficiency_el = float(efficiency_ele/100)
    efficiency_q = float(efficiency_th/100)
    efficiency = float(efficiency_ele/100)
    # demand_h2_kw = float(demand_h2/8760)
    # demand_h2_kg = float(demand_h2/33,3)

    # if input technology is "Grid", there is a zero set as default value for power input and location
    if input_technology == "Grid":
        power_input = 0
        location = 0

    # transforms the input value (EUR/kW or % of CapEx) in value for function (EUR/MW)
    capex_power = capex_power_kw * 1000
    opex_power = opex_power_kw * capex_power_kw * 1000
    capex_technology = capex_technology_kw * 1000
    opex_technology = opex_technology_kw * capex_technology_kw * 1000

    if infrastructure_type == "Tubetrailer":
        capacity_1 = 378  # kg bei 200 bar
        capacity_2 = 774  # kg bei 350 bar
        capacity_3 = 1100  # kg bei 500 bar -> 618 € pro kg
        capex_storage_euro_pro_kg = 500

    elif infrastructure_type == "LNG":
        capex_trailer_spez = 212
        capacity = 4300
        transport_lost_day = 0.015
        capex_storage_euro_pro_kg = 105

    elif infrastructure_type == "Pipeline":
        capex_trailer = 0
        opex_trailer = 0
        capacity = 0
        capex_storage_euro_pro_kg = 0
    else:
        capex_storage_euro_pro_kg = 600

    # the value "renewables" is a True/False-variable that is important for frontend-html: If renewables true, the renewable energy production is shown as a figure
    renewables = False
    if ptx_technology == "Power-to-X":
        if input_technology in list_pp:  # if the input technology is a production plant, the output and dcf are calculated
            renewables = True
            a = output_power_production(input_technology, power_input, location,
                                        share_input_wind, share_input_pv)
            b = dcf_power_production(input_technology, power_input, capex_power, opex_power,
                                     runtime, location, power_cost, power_price_series, wacc, price_change,
                                     share_input_wind, share_input_pv)

    # the output and DCF for a PtX Technology are calculated (for details: functions.py)
        c = output_power_to_x(power_technology, input_technology, efficiency, product_price, margincost_model,
                              variable_cost, location, power_input, power_price_series, price_change,
                              share_input_wind, share_input_pv)
        d = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime,
                           power_cost, power_price_series, variable_cost, product_price,
                           input_technology, power_input, capex_power,
                           opex_power, efficiency, margincost_model, location, wacc, price_change,
                           regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease,
                           share_input_wind, share_input_pv)
        '''sensitivity_PTX = sensitivity_power_to_X(dcf_power_to_x(power_technology, capex_technology, opex_technology,
                                                                runtime, power_cost, power_price_series,
                                                                variable_cost, product_price,
                                                                input_technology, power_input, capex_power, opex_power,
                                                                efficiency, margincost_model, location, wacc,
                                                                price_change, regulations_grid_expenditure,
                                                                EEG_expenditure, capex_decrease, opex_decrease,
                                                                share_input_wind, share_input_pv))'''

    # the output and DCF for a XtP Technology are calculated (for details: functions.py)
    elif ptx_technology == "X-to-Power":
        e = output_x_to_power(power_cost, power_price_series, power_technology,
                              product_price, efficiency_el, efficiency_q,
                              margincost_model, variable_cost, price_change)
        d = dcf_x_to_power(power_technology, capex_technology, opex_technology, runtime,
                           product_price, variable_cost, power_cost, power_price_series, heat_cost,
                           efficiency_el, efficiency_q,
                           margincost_model, wacc, price_change, capex_decrease, opex_decrease)

    # If additional infrastructure for gaseous energy carriers is to be built, the dimensioning and costs are issued here
    # the table creation in the frontend would not run, so here is a default table if no infrastructure is needed
    list1 = list(range(1, 20))
    x = pd.DataFrame({"default": list1, "default": list1})
    h = [x, "default"]
    infrastructure = False
    # storage dimension and costs should be calculated

    # if infrastructure should be dimensioned, the functions g and h are executed
    if do_infrastructure == "yes":
        infrastructure = True
        g = infrastructure_dimension(ptx_technology, do_infrastructure, infrastructure_type, distance, power_technology,
                                     input_technology, efficiency, product_price, margincost_model,
                                     variable_cost, location,
                                     power_input, power_cost, power_price_series,
                                     efficiency_el, efficiency_q, price_change, transport_pressure,
                                     capacity, share_input_wind, share_input_pv)

        h = infrastructure_dcf(ptx_technology, do_infrastructure, infrastructure_type, distance, power_technology,
                               input_technology, efficiency, product_price, margincost_model, variable_cost, location,
                               power_input, power_cost, power_price_series,
                               efficiency_el, efficiency_q, runtime, wacc, price_change,
                               CAPEX_COMPRESSOR_1, CAPEX_COMPRESSOR_2, OPEX_COMPRESSOR_RATE,
                               CAPEX_PIPE_1, CAPEX_PIPE_2, CAPEX_PIPE_3, OPEX_PIPE_RATE, capex_trailer, capex_storage_euro_pro_kg,
                               capex_storagetank, transport_pressure, capacity, opex_trailer, capex_liquifier,
                               opex_liquifier_rate, share_input_wind, share_input_pv, g)

# a graphic is created from the power production profile
    if input_technology in list_pp and ptx_technology in list_ptx:
        plt.figure(1)
        plt.plot('time', 'pv_production', data=a, marker='', color='skyblue', linewidth=1)
        plt.plot('time', 'wind_production', data=a, marker='', color='olive', linewidth=1)
        plt.legend()
        plt.savefig('static/power_production_plot.png')

    return render_template('output.html', runtime=runtime, npv_ptx=d[1], column_names1 = d[0].columns.values,
                           row_data1=list(d[0].values.tolist()),
                           renewables=renewables, ptx_technology=ptx_technology, column_names2 = h[0].columns.values,
                           row_data2=list(h[0].values.tolist()),
                           infrastructure=infrastructure, npv_infrastructure=h[1], zip = zip)


if __name__ == "__main__":
    app.run(debug=True)


