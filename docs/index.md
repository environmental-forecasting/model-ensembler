# model-ensembler
![GitHub issues](https://img.shields.io/github/issues/environmental-forecasting/model-ensembler?style=plastic)
![GitHub closed issues](https://img.shields.io/github/issues-closed/environmental-forecasting/model-ensembler?style=plastic)
![GitHub](https://img.shields.io/github/license/environmental-forecasting/model-ensembler)
![GitHub forks](https://img.shields.io/github/forks/environmental-forecasting/model-ensembler?style=social)
![GitHub forks](https://img.shields.io/github/stars/environmental-forecasting/model-ensembler?style=social)
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

`model-ensembler`is a tool to configure and automate running model ensembles on High-Performance Computing (HPC) clusters.
It reduces the manual configuration of individual ensemble runs, by using a common configuration to individually generate templates
for each run.

It also provides pre-and post processing functionality to allow for common tasks to be applied to the ensemble, before
and after the individual runs. 

`model-ensembler` is developed to be extendable to various HPC backends, but currently it supports SLURM and running locally. 

## What is a model ensemble?
Explanation of ensembles and their value, with WAVI example.

![Simple diagram of an ensemble](images/ensemble.drawio.png#only-dark)
![Simple diagram of an ensemble](images/ensemble.drawio.light.png#only-light)
/// caption
**Figure 1.** An illustrative diagram of a model ensemble.
///

Can be multi-model, or the same model with different configuration/parameters.

## Why use `model-ensembler`?
Why should users use *this* tool.

The example in **Figure 1** is a simple example of an ensemble with just three models, but what if your ensemble has 50 models?
500 models? Setting up the configuration for each ensemble member would bring significant manual overhead.

`model-ensembler` uses a single configuration file, in the form of a `.yml` file, to control your ensemble. The `.yml` relies on
[jinja2](https://jinja.palletsprojects.com/en/stable/) templates 

### Definitions
* **an ensemble:** A collection of models
* **a model:** The individual model 
* **a run:** When a model is being executed, with its given parameters, we refer to it as a run.
* **a job:** Once a run has been submitted to SLURM, we define it as a job. `model-ensembler` can control the number of jobs that
are executed concurrently.
* **a batch:** We refer to the **collection** of runs as a batch.
* **pre-processing:** Common task(s) that are executed _before_ a batch is submitted, for example ingesting and wrangling a common dataset.
* **post-processing:** Common task(s) that are executed _after_ a batch has completed execution, for example aggregating results.

...submit them to SLURM **asynchronously**.

See the [testimonials](testimonials.md) to get a flavour of the types of model ensembles `model-ensembler` has been used for.

## Environmental Forecasting
The `model-ensembler` is part of a wider family of tools for [Environmental Forecasting](https://github.com/environmental-forecasting):

* [download-toolbox](https://github.com/environmental-forecasting/download-toolbox)
* [preprocess-toolbox](https://github.com/environmental-forecasting/preprocess-toolbox)