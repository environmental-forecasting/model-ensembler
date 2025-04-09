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

More info on ensembles...

## Why use `model-ensembler`?
Why should users use *this* tool.

The example in **Figure 1** is a simple example of an ensemble with just three models, but what if your ensemble has 10, 100 or
1000 models? Setting up the configuration for each ensemble member would bring significant manual overhead.

`model-ensembler` uses a single ensemble configuration file, in the form of a `.yml` file, and a collection of
[jinja2](https://jinja.palletsprojects.com/en/stable/) templates to control your ensemble and dynamically generate
a batch (or batches) of model runs. 

=== "Single Batch"

    ![Single batch overview, dark mode](images/model-ensembler.drawio.png#only-dark)
    ![Single batch overview, light mode](images/model-ensembler.drawio.light.png#only-light)

=== "List of Batches"
    ![List batch overview, dark mode](images/model-ensembler-list.drawio.png#only-dark)
    ![List batch overview, light mode](images/model-ensembler-list.drawio.light.png#only-light)

/// caption
**Figure 2.** A simplified overview of how `model-ensembler` dynamically generates an ensemble run based on a `config.yml` and `jinja2` templates.
///

This design means writing a `config.yml` and corresponding templates just once, and intents to give provide flexibility and enable a 
wide range of applications.

Jump into the [Basic Usage](user/basic-usage.md) to get started, and refer to [Building Configuration & Templates](user/templates.md) for guidance on creating your own configurations.

## Examples and Testimonials
Example configurations and templates are provided under `examples/`, and documented under [Example Section](user/example1.md) (to be renamed).

Also take a look at the [testimonials](testimonials.md) page to get a flavour of the types of model ensembles `model-ensembler` has been used for.

## Environmental Forecasting
The `model-ensembler` is part of a wider family of tools for [Environmental Forecasting](https://github.com/environmental-forecasting):

* [download-toolbox](https://github.com/environmental-forecasting/download-toolbox): A toolbox of downloaders for environmental data.
* [preprocess-toolbox](https://github.com/environmental-forecasting/preprocess-toolbox): A toolbox for processing downloaded datasets according to common approaches for environmental data.