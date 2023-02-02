'''
Tool for economical evaluation of sector coupling business models
Databank File: Imports the necessary data-rows as csv.-file

SPDX-FileCopyrightText: Arian Hohgraeve <a.e.hohgraeve@web.de>
                        Johannes Giehl

SPDX-License-Identifier: MIT

'''


import pandas as pd


# import the cost data for power supply and heat supply EINHEIT: €/MWh
def get_price_series(power_price_series):
    electricity_cost_data = pd.read_csv(
        f"databank/Strom_Kosten_{power_price_series}.csv")  # change year and type for other series
    return electricity_cost_data


heat_cost_data = pd.read_csv("databank/Heat_Kosten_2020.csv")

# various .csv-data for the production capacity per kW for power production (PV, Wind) for various German states
brandenburg_solar_data = pd.read_csv("databank/NINJA_PV_Brandenburg.csv")
berlin_solar_data = pd.read_csv("databank/NINJA_PV_Berlin.csv")
hamburg_solar_data = pd.read_csv("databank/NINJA_PV_Hamburg.csv")
saarland_solar_data = pd.read_csv("databank/NINJA_PV_Saarland.csv")
niedersachsen_solar_data = pd.read_csv("databank/NINJA_PV_Niedersachsen.csv")
mecklenburgvorpommern_solar_data = pd.read_csv("databank/NINJA_PV_MecklenburgVorpommern.csv")
nordrheinwestphalen_solar_data = pd.read_csv("databank/NINJA_PV_NordrheinWestphalen.csv")
bayern_solar_data = pd.read_csv("databank/NINJA_PV_Bayern.csv")
sachsen_solar_data = pd.read_csv("databank/NINJA_PV_Sachsen.csv")
badenwuerttemberg_solar_data = pd.read_csv("databank/NINJA_PV_BadenWuerttemberg.csv")
rheinlandpfalz_solar_data = pd.read_csv("databank/NINJA_PV_RheinlandPfalz.csv")
hessen_solar_data = pd.read_csv("databank/NINJA_PV_Hessen.csv")
schleswigholstein_solar_data = pd.read_csv("databank/NINJA_PV_SchleswigHolstein.csv")
thueringen_solar_data = pd.read_csv("databank/NINJA_PV_Thueringen.csv")
sachsenanhalt_solar_data = pd.read_csv("databank/NINJA_PV_SachsenAnhalt.csv")
bremen_solar_data = pd.read_csv("databank/NINJA_PV_Bremen.csv")

brandenburg_wind_data = pd.read_csv("databank/NINJA_Wind_Brandenburg.csv")
berlin_wind_data = pd.read_csv("databank/NINJA_Wind_Berlin.csv")
hamburg_wind_data = pd.read_csv("databank/NINJA_Wind_Hamburg.csv")
saarland_wind_data = pd.read_csv("databank/NINJA_Wind_Saarland.csv")
niedersachsen_wind_data = pd.read_csv("databank/NINJA_Wind_Niedersachsen.csv")
mecklenburgvorpommern_wind_data = pd.read_csv("databank/NINJA_Wind_MecklenburgVorpommern.csv")
nordrheinwestphalen_wind_data = pd.read_csv("databank/NINJA_Wind_NordrheinWestphalen.csv")
bayern_wind_data = pd.read_csv("databank/NINJA_Wind_Bayern.csv")
sachsen_wind_data = pd.read_csv("databank/NINJA_Wind_Sachsen.csv")
badenwuerttemberg_wind_data = pd.read_csv("databank/NINJA_Wind_BadenWuerttemberg.csv")
rheinlandpfalz_wind_data = pd.read_csv("databank/NINJA_Wind_RheinlandPfalz.csv")
hessen_wind_data = pd.read_csv("databank/NINJA_Wind_Hessen.csv")
schleswigholstein_wind_data = pd.read_csv("databank/NINJA_Wind_SchleswigHolstein.csv")
thueringen_wind_data = pd.read_csv("databank/NINJA_Wind_Thueringen.csv")
sachsenanhalt_wind_data = pd.read_csv("databank/NINJA_Wind_SachsenAnhalt.csv")
bremen_wind_data = pd.read_csv("databank/NINJA_Wind_Bremen.csv")

list_ort = ["Brandenburg", "Berlin", "Hamburg", "Saarland", "Niedersachsen",
         "Mecklenburg Vorpommern", "Nordrhein Westphalen", "Bayern", "Baden Württemberg",
        "Rheinland Pfalz", "Hessen", "Thüringen", "Sachsen", "Schleswig Holstein", "Sachsen Anhalt", "Bremen"]


dict_ort = {
    "Brandenburg": (brandenburg_solar_data, brandenburg_wind_data),
    "Berlin" : (berlin_solar_data, berlin_wind_data),
    "Hamburg" : (hamburg_solar_data, hamburg_wind_data),
    "Saarland" : (saarland_solar_data, saarland_wind_data),
    "Niedersachsen" : (niedersachsen_solar_data, niedersachsen_wind_data),
    "Mecklenburg Vorpommern" : (mecklenburgvorpommern_solar_data, mecklenburgvorpommern_wind_data),
    "Nordrhein Westphalen": (nordrheinwestphalen_solar_data, nordrheinwestphalen_wind_data),
    "Bayern" : (bayern_solar_data, bayern_wind_data),
    "Baden Württemberg" : (badenwuerttemberg_solar_data, badenwuerttemberg_wind_data),
    "Rheinland Pfalz" : (rheinlandpfalz_solar_data, rheinlandpfalz_wind_data),
    "Hessen" : (hessen_solar_data, hessen_wind_data),
    "Thüringen": (thueringen_solar_data, thueringen_wind_data),
    "Sachsen" : (sachsen_solar_data, sachsen_wind_data),
    "Schleswig Holstein" : (schleswigholstein_solar_data, schleswigholstein_wind_data),
    "Sachsen Anhalt" : (sachsenanhalt_solar_data, sachsenanhalt_wind_data),
    "Bremen" : (bremen_solar_data, bremen_wind_data)
}
