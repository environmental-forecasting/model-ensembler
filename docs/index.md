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

The example in **Figure 1** is a simple example of an ensemble with just three models, but what if your ensemble has 10,100 or
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
**Figure 2.** A simplified overview of how `model-ensembler` dynamically generates an ensemble based on a `config.yml` and `jinja2` templates.
///

For the user, this setup means writing a `config.yml` and corresponding templates just once. `model-ensembler` is light-weight,
and intents to give the user flexibility in giving them control in developing their own configuration and templates.

### Definitions
Before we dive into an overview of how `model-ensembler` works, some important definitions that will be used throughout:

* **a batch:** We refer to the **collection** of runs as a batch. `model-ensembler` can be used to configure a _single_ batch
or a _list_ of batches. **Figure 1** can be interpreted as a single batch.
* **a run:** Each _batch_ controls a set of model runs.
* **a model:** The individual model to be executed by a run.
* **a job:** Once a run has been submitted to SLURM, we define it as a job. It is distinguished from a run,
as `model-ensembler` enables configuration that can control the number of jobs that are executed concurrently
on an HPC cluster.
* **pre-processing:** Common task(s) that are executed _before_ batch execution.
* **post-processing:** Common task(s) that are executed _after_ batch completion.

```bash
├── templates/
│   ├── inputfile.j2
│   ├── preprocess.sh.j2
│   ├── slurm_run.sh.js
│   └── postprocess.sh.j2
└── ensemble_config.yml
```

```yaml
ensemble:
    vars: []
    pre_process: []
    post_process: []

    batch_config:
        templates:
        - inputfile.j2
        - preprocess.sh.j2
        - slurm_run.sh.j2
        - postprocess.sh.j2
        cluster: []
        nodes: []
        ntasks: []

    batches:
        - name: batch_1
          pre_run: []
          runs:
            - custom_id: 1
            - custom_id: 2
          post_run: []
        - name: batch_2
          pre_run: []
          runs:
            - custom_id: 1
            - custom_id: 2
          post_run: []
```

...submit them to SLURM **asynchronously**.

See the [testimonials](testimonials.md) to get a flavour of the types of model ensembles `model-ensembler` has been used for.

## Environmental Forecasting
The `model-ensembler` is part of a wider family of tools for [Environmental Forecasting](https://github.com/environmental-forecasting):

* [download-toolbox](https://github.com/environmental-forecasting/download-toolbox)
* [preprocess-toolbox](https://github.com/environmental-forecasting/preprocess-toolbox)