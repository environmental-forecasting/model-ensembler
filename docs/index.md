# model-ensembler
[//]: # (Part of this .md is generated frm the README)
--8<-- "README.md:2:61"

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

This design means writing a `config.yml` and corresponding templates just once, and intents to provide flexibility and enable a 
wide range of applications.

## Where to go from here
The idea of `model-ensembler` is to give you the flexibility to set this up for your
own ensembles.

The basic pattern for using this toolkit is:

1. Adapt job/model run templates 
1. Adapt YAML Configuration
1. Running the job using `model_ensemble`

Jump into [Building Configuration & Templates](user/templates.md) for guidance on creating your own configurations.

## Examples and Testimonials
Example configurations and templates are provided under `examples/`, and documented under [Example Section](user/example1.md) (to be renamed).

Also take a look at the [testimonials](testimonials.md) page to get a flavour of the types of model ensembles `model-ensembler` has been used for.