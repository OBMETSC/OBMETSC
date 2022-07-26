## Table of Contents
1. [General Info](#general-info)
2. [Setup](#setup)
4. [Usage](#usage)
5. [Transformation](#transformation)

### General Info
***
Tool for economical evaluation of sector coupling business models 

Functions File: The functions include the mathematical calculation logic for determining the production and profitability

SPDX-FileCopyrightText: Arian Hohgraeve <a.e.hohgraeve@web.de>

SPDX-License-Identifier: MIT
## Setup
***
For the setup, a virtual environment must be set up, which contains the following programs and libraries:
* [python]: version 3.8.8
* [flask]: version 1.1.2
* [flask-wtf]: version 0.15.1
* [Flask]: version 1.1.2
* [jinja2]: version 2.11.3
* [matplotlib]: version 3.3.4
* [matplotlib-base]: version 3.3.4
* [numpy]: version 1.19.2
* [numpy-base]: version 1.19.2
* [pandas]: version 1.2.3
* [pip]: version 21.0.1
* [werkzeug]: version 1.0.1

In addition to the programs and libraries described above, it is assumed that the standard Python applications are 
included in the virtual environment.

At startup, only the main.py file must be executed. The file accesses all other files and libraries itself.

## Usage
***
For use, any development and compilation environment for Python can be used. However, the application has been tested 
only in PyCharm.2021.1.3 so far.

Running main.py produces the following result:

> * Debug mode: on
> * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
> * Restarting with stat
> * Debugger is active!
> * Debugger PIN: 429-176-169

The web path http://127.0.0.1:5000/ can be used to retrieve the generated server on which the web application is served.

To open the web application you only need a browser that supports html (e.g. Mozilla Firefox, Safari, Google Chrome or 
Internet Explorer in current version).

When the web application is successfully accessed, the tool can be operated intuitively.

## Transformation
***
Despite the generic input values, it is assumed that some values can be exchanged in the application.

For easier editing, the following is a brief summary of where certain parameters and calculations can be found.
* In addition to editing py-files, production and price profiles can also be edited and replaced. For this, the csv.files in the ".../databank" folder must be edited.

| File | Line | Content |
|:--------------|:-------------:|--------------:|
| main.py | 37 - 64 | Import and transformation of data from the input of the web application |
| main.py | 77 - 95 | Conversion of the inputs into the units of the calculation |
| main.py | 98 - 129 | Hardcopy values for infrastructure. Can be customized! |
| main.py | 131 - 176 | Execution of the functions from functions.py with the input values |
| main.py | 178 - 184 | Generation of a picture to visualize the RE power production profile |
| main.py | 187 - 189 | Output of functions is rendered to get exported to output.html. If functions are added or deleted, the render-function has to be changed|
| functions.py | 20 - 43 | Function for calculating the output from electricity production |
| functions.py | 46 - 88 | Function for calculating the profitability of electricity production |
| functions.py | 93 - 188 | Function to calculate the output from Power-to-X plant |
| functions.py | 191 - 276 | Function for calculating the economic efficiency of power-to-X plants |
| functions.py | 280 - 312 | Function to calculate the output from X-to-Power plant |
| functions.py | 316 - 382 | Function for calculating the economic efficiency of the X-to-Power plant |
| functions.py | 386 - 441 | Function for calculating the dimensioning of the H2 infrastructure |
| functions.py | 444 - 523 | Function for calculating the economic efficiency of the H2 infrastructure |
| databank.py | 17 | Import of csv-file for elecrticity cost profile over one year. File path can be changed for alternative profile. |
| databank.py | 18 | Import of csv-file for heat cost profile over one year. File path can be changed for alternative profile. |
| databank.py | 20 - 53 | Import of csv-files for PV and wind production profiles for every region in Germany over one year. File path can be changed for alternative profile. |
| databank.py | 55 - 77 | Library and list for simplified access of the functions to the profiles of the different regions |

