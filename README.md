# ``commute``


Prospective life cycle assessment of passenger and freight transport.

A fully parameterized Python model developed by the [Technology Assessment group](https://www.psi.ch/en/ta) of the
[Paul Scherrer Institut](https://www.psi.ch/en) to perform life cycle assessments (LCA) of passenger and freight vehicles.
It merges `carculator`, `carculator_two_wheeler`, `carculator_truck`, 
and `carculator_bus` libraries to provide a single interface to perform LCA of passenger and freight vehicles.

See [the documentation](https://commute.readthedocs.io/en/latest/index.html) for more detail, validation, etc.

See our [examples notebook](https://github.com/romainsacchi/commute/blob/master/examples/Examples.ipynb) as well.

## Table of Contents

- [Background](#background)
  - [What is Life Cycle Assessment](#what-is-life-cycle-assessment)
  - [Why commute](#why-commute)
- [Install](#install)
- [Usage](#usage)
  - [As a Python library](#as-a-python-library)
  - [As a web app](#as-a-web-app)
- [Support](#support)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Background

### What is Life Cycle Assessment?

Life Cycle Assessment (LCA) is a systematic way of accounting for environmental impacts along the relevant phases of the life of a product or service.
Typically, the LCA of a passenger vehicle includes the raw material extraction, the manufacture of the vehicle, its distribution, use and maintenance, as well as its disposal.
The compiled inventories of material and energy required along the life cycle of the vehicle is characterized against some impact categories (e.g., climate change).

In the research field of mobility, LCA is widely used to investigate the superiority of a technology over another one.

### Why ``commute``?

``commute`` allows to:
* produce [life cycle assessment (LCA)](https://en.wikipedia.org/wiki/Life-cycle_assessment) results that include midpoint and endpoint impact assessment indicators
*  ``commute`` uses time- and energy scenario-differentiated background inventories for the future, based on outputs of Integrated Asessment Model [REMIND](https://www.pik-potsdam.de/research/transformation-pathways/models/remind/remind). 
* calculate hot pollutant and noise emissions based on a specified driving cycle
* produce error propagation analyzes (i.e., Monte Carlo) while preserving relations between inputs and outputs
* control all the parameters sensitive to the foreground model (i.e., the vehicles) but also to the background model
(i.e., supply of fuel, battery chemistry, etc.)
* and easily export the vehicle models as inventories to be further imported in the [Brightway2](https://brightwaylca.org/) LCA framework
  or the [SimaPro](https://www.simapro.com/) LCA software.

``commute`` integrates well with the [Brightway](https://brightwaylca.org/) LCA framework.

``commute`` was built based on the following  studies:
* [Uncertain environmental footprint of current and future battery electric vehicles by Cox et al. (2018)](https://pubs.acs.org/doi/abs/10.1021/acs.est.8b00261).
* [When, where and how can the electrification of passenger cars reduce greenhouse gas emissions? by Sacchi et al. (2022)](https://www.sciencedirect.com/science/article/pii/S136403212200380X)
* [Does Size Matter? The Influence of Size, Load Factor, Range Autonomy, and Application Type on the Life Cycle Assessment of Current and Future Medium- and Heavy-Duty Vehicles, by Sacchi et al. (2022)](https://pubs.acs.org/doi/abs/10.1021/acs.est.0c07773)

## Install

``commute`` is at an early stage of development and is subject to continuous change and improvement.
Three ways of installing ``commute`` are suggested.

We recommend the installation on **Python 3.9 or above**.

### Installation of the latest version, using conda

    conda install -c romainsacchi commute

### Installation of a stable release (1.3.1) from Pypi

    pip install commute


## Support

Do not hesitate to contact the development team at [carculator@psi.ch](mailto:carculator@psi.ch).

## Maintainers

* [Romain Sacchi](https://github.com/romainsacchi)
* [Chris Mutel](https://github.com/cmutel/)

## Contributing

See [contributing](https://github.com/romainsacchi/commute/blob/master/CONTRIBUTING.md).

## License

[BSD-3-Clause](https://github.com/romainsacchi/commute/blob/master/LICENSE). Copyright 2020 Paul Scherrer Institut.
