# OBMETSC
**An open source tool to evaluate sector coupling business models** 

## Contents
* [Introduction](#introduction)
* [Documentation](#documentation)
* [Installation](#installation)
* [Contributing](#contributing)
* [Citing](#citing)
* [License](#license)

## Introduction
**OBMETSC** is a tool and database to evaluate business models of sector coupling. The tool was originally developed by a group of researchers and students at the [chair of Energy and Resources Management of TU Berlin](https://www.er.tu-berlin.de/menue/home/) and is now maintained by a group of alumni and open for other contributions. The focus lies on the German Energy Market but the tool itsels allows also generic calculations for other regions. 

### Purpose and model background
**OBMETSC** provides a generic platform for evaluating a wide range of business models for sector coupling. It allows the user to fill in her own use cases with her own assumptions via an HTML-based interface and to evaluate the economic success. A database also allows access to information on existing technologies and market conditions. The status quo is given in the case of electricity prices for Germany and weather data for the German federal states. 

The models' overall goal is to compute an net present value for the choosen business model (Power-to-X or X-to-Power). Constraints such as electricity supply by renewable energies are considered.  Thus, the model purpose is to privide a tool that allows an easy assessmet of the market chances of sector coupling business models. 

## Documentation
An upcoming and extensive **[documentation of OBMETSC](https://OBMETSC.readthedocs.io/)** can be found on readthedocs. It will contain a user's guide, a model categorization, some energy economic and technical background information, a complete model formulation as well as documentation of the model functions and classes. 

## Installation

### Setting up OBMETSC
`OBMETSC` can bes installed via pip. 
To install it, please use the following command
```
pip install git+https://github.com//OBMETSC/OBMETSC/
```

If you want to contribute as a developer, you fist have to
[fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo>)
it and then clone the repository, in order to copy the files locally by typing
```
git clone https://github.com/your-github-username/OBMETSC.git
```
After cloning the repository, you have to install the required dependencies.
Make sure you have conda installed as a package manager.
If not, you can download it [here](https://www.anaconda.com/).
Open a command shell and navigate to the folder

## Contributing
Every kind of contribution or feedback is warmly welcome.<br>
We use the [GitHub issue management](https://github.com/OBMETSC/OBMETSC/issues) as well as 
[pull requests](https://github.com/OBMETSC/OBMETSC/pulls) for collaboration. We try to stick to the PEP8 coding standards.

The following people have contributed in the following manner to `OBMETSC`:

| Name | Contribution | Status |
| ---- | ---- | ---- |
| Johannes Giehl | major development & conceptualization, core functionality, architecture, publishing process | coordinator, maintainer, developer & corresponding author |
| Arian Hohgräve | major development & conceptualization, core functionality, architecture | coordinator & developer |
| Melina Lohmann | further development, core functionality | developer |
| Joachim Müller-Kirchenbauer | support & early-stage conceptualization, funding | supporter (university professor) |

## Citing
A publication using and introducing `OBMETSC` is currently in preparation.

If you are using `OBMETSC` for your own analyses, we recommend citing as:<br>
*Giehl, J.; Hohgräve, A. et al. (2021): OBMETSC. An open source tool to evaluate sector coupling business models. https://github.com/OBMETSC/OBMETSC, accessed YYYY-MM-DD.*

We furthermore recommend naming the version tag or the commit hash used for the sake of transparency and reproducibility.

Also see the *CITATION.cff* file for citation information.

## License
This software is licensed under MIT License.

Copyright 2022 OBMETSC developer group

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
