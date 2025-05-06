# Model Ensembler
![GitHub issues](https://img.shields.io/github/issues/environmental-forecasting/model-ensembler?style=plastic)
![GitHub closed issues](https://img.shields.io/github/issues-closed/environmental-forecasting/model-ensembler?style=plastic)
![GitHub](https://img.shields.io/github/license/environmental-forecasting/model-ensembler)
![GitHub forks](https://img.shields.io/github/forks/environmental-forecasting/model-ensembler?style=social)
![GitHub forks](https://img.shields.io/github/stars/environmental-forecasting/model-ensembler?style=social)
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

`model-ensembler`is a tool to configure and automate running model ensembles on High-Performance Computing (HPC) clusters.
It reduces the manual configuration of individual ensemble runs, by using a common configuration to individually generate templates
for each run.

It also provides pre-and post processing functionality to allow for common tasks to be applied to the ensemble, before
and after the individual runs. 

`model-ensembler` is developed to be extendable to various HPC backends,currently supporting SLURM and running locally. 

## Installation
To install `model-ensembler`:
```
python -m venv venv
source venv/bin/activate
pip install model-ensembler
```

To check it has installed correctly, you can run:
```
model_ensemble_check [dummy|slurm]
```

## Basic Usage
Under the `examples/` folder you will find example configs and templates that we can run on a local machine:

```shell
examples/
├── template_job/
│   ├── inputfile.j2
│   ├── pre_run.sh.j2
│   ├── slurm_run.sh.js
│   └── post_run.sh.j2
└── ensemble_config.yml
```

The command `model_ensemble` is provided to execute the ensemble.

The `--help` flag can be used to find out more information:

```shell
model_ensemble --help
```
Its use is as follows:

```shell
model_ensemble configuration {slurm, dummy}
```

Here `configuration` refers to our configuration file, and `{slurm, dummy}`
are the HPC backend options (where `dummy` is the options to run locally). 

Applying this to our `examples/`, and running locally:

```shell
model_ensemble examples/sanity-check.yml dummy
```

You are now running a model ensemble!

## Documentation
For further usage instructions and an overview of `model-ensembler`, please refer to the documentation.

## Future plans
Current plans are captured now in the github issues. There's nothing in the 
long term that I'm focusing on for this tool, except to maintain it and see 
if I can promote the usage a bit more. 

This tool was merely to help out with a single support ticket for a weather 
model run, but the concept had potential and it was easier than deploying 
something more substantial! If there are better approaches or tools that do 
something similar, very keen to look at them! 

Certainly, things like Airflow and job arrays have similar concepts, but are 
either more heavyweight/less suitable deployment wise or not abstracted enough 
for simplifying lives, respectively!!!

## Cylc

Compare [Cylc](https://cylc.github.io/) to `model-ensembler`. 

## Environmental Forecasting
The `model-ensembler` is part of a wider family of tools for [Environmental Forecasting](https://github.com/environmental-forecasting):

* [download-toolbox](https://github.com/environmental-forecasting/download-toolbox): A toolbox of downloaders for environmental data.
* [preprocess-toolbox](https://github.com/environmental-forecasting/preprocess-toolbox): A toolbox for processing downloaded datasets according to common approaches for environmental data.

## Copyright
[MIT LICENSE](LICENSE)

&copy; British Antarctic Survey 2021-2025

