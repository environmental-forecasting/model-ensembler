# model-ensembler
[//]: # (Part of this .md is generated frm the README)
--8<-- "README.md:2:66"

## What is a model ensemble?
![Simple diagram of an ensemble](images/ensemble.drawio.png#only-dark)
![Simple diagram of an ensemble](images/ensemble.drawio.light.png#only-light)
/// caption
**Figure 1.** An illustrative diagram of a model ensemble.
///

Rather than running a single model, we run a model (or multiple models) many times. This is useful when there is high uncertainty around parameters that can  affect model predictions. This could be to do with the model physics itself ([Bett et al. 2025](https://tc.copernicus.org/articles/18/2653/2024/)), but also the initialisation date, resolution ([Williams et al. 2025](https://tc.copernicus.org/articles/18/2653/2024/)) or the input datasets being used.

Ensembles can also be multi-model ([Seroussi et al. 2020](https://tc.copernicus.org/articles/14/3033/2020/)), or a comparison between different scenario ensembles (e.g. anthropogenic vs counterfactual in ([Bradley et al. 2024](https://www.nature.com/articles/s43247-024-01287-w#Sec7))).

## Why use `model-ensembler`?
The example in **Figure 1** is a simple example of an ensemble with just three models (or _members_), but what if your ensemble has 10, 100 or
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

This design means writing a `config.yml` and corresponding templates just once, and intents to provide flexibility and enable a 
wide range of applications.

## Multiple batches
Figure 2 shows an example of a single batch ensemble, or a list of batches. But why would you need multiple batches?

Multiple batch functionality exists for instances where there is a need to run similar, but different
ensembles. Perhaps they have identical input files, domain, but compare different forcing or resolutions.

!!! example "Multiple batch example: estimating the anthropogenic part of Antarctica's sea level contribution"

    [Bradley, A.T., Bett, D.T., Holland, P.R. et al. Author Correction: A framework for estimating the anthropogenic part of Antarctica’s sea level contribution in a synthetic setting. Commun Earth Environ 5, 429 (2024)](https://doi.org/10.1038/s43247-024-01600-7) contains an example where two batches of an ice sheet model under different forcing are used to estimate the anthropogenic
    part of Antarctica's sea level contribution.

## Where to go from here
The idea of `model-ensembler` is to give you the flexibility to set this up for your
own ensembles.

The basic pattern for using this toolkit is:

1. Adapt job/model run templates 
1. Adapt YAML Configuration
1. Running the job using `model_ensemble`

Jump into [Building Configuration & Templates](user/templates.md) for guidance on creating your own configurations.

## Examples and Testimonials
Example configurations and templates are provided under `examples/`. A worked example is provided under
[Simple Example - WAVI](user/WAVI_example.md).

Also take a look at the [testimonials](testimonials.md) page to get a flavour of the types of model ensembles `model-ensembler` has been used for.