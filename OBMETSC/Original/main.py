import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from functions import *
from flask import Flask, render_template, request

#the lists are necessary to make if-else-actions depending on the technology
list_ptx = ["Power-to-X"] # Power-to-X technologies
list_xtp = ["X-to-Power"] # X-to-Power technologies
list_pp = ["PV", "Wind", "PV+Grid", "Wind+Grid", "Wind+PV"] # input-technologies, based on renewable power production

#creats the webapp with a secret key
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisisasecret'

#the app.route starts an index page which welcomes the user (compare: index.html)
@app.route('/')
def index():
    return render_template("index.html")

#the database page can be selected and gives back the background informations about the tool
@app.route('/database')
def database():
    return render_template("database.html")

#app route that leads user to the tool input page
@app.route('/calculator', methods=['GET', 'POST'])
def input():
    return render_template("input.html")

#this app route shows the results of the tool and appears when you have submit the input
@app.route('/output', methods=['GET', 'POST'])
def get():

#the following variables are getting the informations from the input.html page
    ptx_technology = str(request.form['ptx_technology'])
    capex_technology = int(request.form['capex_technology'])
    opex_technology = int(request.form['opex_technology'])
    variable_cost = int(request.form['variable_cost'])
    efficiency_ele = int(request.form['efficiency_ele'])
    efficiency_th = int(request.form['efficiency_th'])
    power_technology = int(request.form['power_technology'])
    capex_input = int(request.form['capex_input'])
    opex_input = int(request.form['opex_input'])
    power_cost = int(request.form['power_cost'])
    heat_cost = int(request.form['heat_cost'])
    margincost_model = str(request.form['margincost_model'])
    input_technology = str(request.form['input_technology'])
    power_input = int(request.form['power_input'])
    location = str(request.form['location'])
    power_price_change = int(request.form['power_price_change'])
    infrastructure_type = str(request.form['infrastructure_type'])
    distance = int(request.form['distance'])
    EEG_reduction = int(request.form['EEG_reduction'])
    stromsteuer_reduction = int(request.form['stromsteuer_reduction'])
    KWKG_reduction = int(request.form['KWKG_reduction'])
    netzentgelte_reduction = int(request.form['netzentgelte_reduction'])
    capex_subvention = int(request.form['capex_subvention'])
    opex_subvention = int(request.form['opex_subvention'])
    wacc_input = int(request.form['wacc_input'])
    product_price = int(request.form['product_price'])
    runtime = int(request.form['runtime'])
    do_infrastructure = str(request.form['do_infrastructure'])

#changes the input date in the needed form for calculation (e.g.: 5% --> 0.05)
    wacc = (wacc_input / 100)  # turning the input wacc (e.g. 5%) into decimal number (e.g. 0.05)
    price_change = 1 + power_price_change / 100  # turning input price_change (e.g. 5%) into decimal number (e.g. 1.05)
    EEG_expenditure = 65 * (EEG_reduction / 100)  # price for MWh power, reduced with input
    stromsteuer_expenditure = 20.5 * (stromsteuer_reduction / 100)
    KWKG_expenditure = 2.26 * (KWKG_reduction / 100)
    netzentgelte_expenditure = (3.58 + 4.16 + 0.07 + 20) * netzentgelte_reduction / 100   # sum of expenditure from StromNEV, Offshore, Abschaltbare Anlagen, Konzession
    regulations_grid_expenditure = stromsteuer_expenditure + KWKG_expenditure + netzentgelte_expenditure
    capex_decrease = float(1 - (capex_subvention / 100))
    opex_decrease = float(1 - (opex_subvention / 100))

    #the values are translated into the variables for the functions, efficiency is set as electrical efficiency
    capex_power_kw = capex_input
    opex_power_kw = float(opex_input/100)
    capex_technology_kw = capex_technology
    opex_technology_kw = float(opex_technology/100)
    efficiency_el = float(efficiency_ele/100)
    efficiency_q = float(efficiency_th/100)
    efficiency = float(efficiency_ele/100)

    #if input technology is "Grid", there is a zero set as default value for power input and location
    if input_technology == "Grid":
        power_input = 0
        location = 0

    # transforms the input value (EUR/kW or % of CapEx) in value for function (EUR/MW)
    capex_power = capex_power_kw * 1000
    opex_power = opex_power_kw * capex_power_kw * 1000
    capex_technology = capex_technology_kw * 1000
    opex_technology = opex_technology_kw * capex_technology_kw * 1000

    # cost databasis for infastructure
    capex_compressor_1 = 300000 * 0.046
    capex_compressor_2 = 350000 * 0.157
    opex_compressor_rate = 0.75

    capex_liquifier = 7200
    opex_liquifier_rate = 0.76

    capex_pipe_1 = 1200000
    capex_pipe_2 = 1500000
    capex_pipe_3 = 2800000
    opex_pipe_rate = 0.01


    capex_storagetank = 100000

    if infrastructure_type == "Tubetrailer":
        transport_pressure = 400
        capex_trailer = 150000
        opex_trailer = 75000
        capacity = 400

    elif infrastructure_type == "LNG":
        transport_pressure = 0
        capex_trailer = 750000
        opex_trailer = 75000
        capacity = 1200

    elif infrastructure_type == "Pipeline":
        transport_pressure = 20
        capex_trailer = 0
        opex_trailer = 0
        capacity = 0

    #the value "renewables" is a True/False-variable that is important for frontend-html: If renewables true, the renewable energy production is shown as a figure
    renewables = False
    if ptx_technology == "Power-to-X":
        if input_technology in list_pp:#if the input technology is a production plant, the output and dcf are calculated
            renewables = True
            a = output_power_production(input_technology, power_input, location)
            b = dcf_power_production(input_technology, power_input, capex_power, opex_power,
                                     runtime, location, power_cost, wacc, price_change)

    #the output and DCF for a PtX Technology are calculated (for details: functions.py)
        c = output_power_to_x(power_technology, input_technology, efficiency, product_price, margincost_model,
                              variable_cost, location, power_input, price_change)
        d = dcf_power_to_x(power_technology, capex_technology, opex_technology, runtime,
                           power_cost, variable_cost, product_price, input_technology, power_input, capex_power,
                           opex_power, efficiency, margincost_model, location, wacc, price_change,
                           regulations_grid_expenditure, EEG_expenditure, capex_decrease, opex_decrease)

    #the output and DCF for a XtP Technology are calculated (for details: functions.py)
    elif ptx_technology == "X-to-Power":
        e = output_x_to_power(power_cost, power_technology, product_price, efficiency_el, efficiency_q,
                              margincost_model, variable_cost, price_change)
        d = dcf_x_to_power(power_technology, capex_technology, opex_technology, runtime,
                           product_price, variable_cost, power_cost, heat_cost, efficiency_el, efficiency_q,
                           margincost_model, wacc, price_change, capex_decrease, opex_decrease)

    # If additional infrastructure for gaseous energy carriers is to be built, the dimensioning and costs are issued here
    # the table creation in the frontend would not run, so here is a default table if no infrastructure is needed
    list1 = list(range(1, 20))
    x = pd.DataFrame({"default": list1, "default": list1})
    h = [x, "default"]
    infrastructure = False

    #if infrastructure should be dimensioned, the functions g and h are executed
    if do_infrastructure == "yes":
        infrastructure = True
        g = infrastructure_dimension(ptx_technology, infrastructure_type, distance, power_technology,
                                     input_technology, efficiency, product_price, margincost_model, variable_cost, location,
                                     power_input, power_cost, efficiency_el, efficiency_q, price_change, transport_pressure,
                                     capacity)

        h = infrastructure_dcf(ptx_technology, infrastructure_type, distance, power_technology,
                               input_technology, efficiency, product_price, margincost_model, variable_cost, location,
                               power_input, power_cost, efficiency_el, efficiency_q, runtime, wacc, price_change,
                               capex_compressor_1, capex_compressor_2, opex_compressor_rate,
                               capex_pipe_1, capex_pipe_2, capex_pipe_3, opex_pipe_rate, capex_trailer,
                               capex_storagetank, transport_pressure, capacity, opex_trailer, capex_liquifier, opex_liquifier_rate)

#a graphic is created from the power production profile
    if input_technology in list_pp and ptx_technology in list_ptx:
        plt.figure(1)
        plt.plot('time', 'pv_production', data=a, marker='', color='skyblue', linewidth=1)
        plt.plot('time', 'wind_production', data=a, marker='', color='olive', linewidth=1)
        plt.legend()
        plt.savefig('static/power_production_plot.png')


    return render_template('output.html', runtime=runtime, npv_ptx=d[1], column_names1 = d[0].columns.values, row_data1 = list(d[0].values.tolist()),
                           renewables=renewables, ptx_technology=ptx_technology, column_names2 = h[0].columns.values, row_data2 = list(h[0].values.tolist()),
                           infrastructure=infrastructure, npv_infrastructure=h[1], zip = zip)

if __name__ == "__main__":
    app.run(debug=True)
