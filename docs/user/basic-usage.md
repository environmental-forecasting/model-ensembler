# Usage

## Definitions
Before we dive into an overview of how `model-ensembler` works, some important definitions that will be used throughout:


![Definitions diagram, dark mode](../images/definitions.drawio.png#only-dark)
![Definitions diagram, light mode](../images/definitions.drawio.light.png#only-light)
/// caption
**Figure 1:** Visual overview of the definitions used throughout `model-ensembler` documentation.
///

For the ensemble:

* **a model:** The individual model to be executed by a run.
* **a run:** A run refers to the execution of a model, with a given set of parameters.
* **a batch:** We refer to the collection of model runs as a batch. `model-ensembler` can be used to configure a _single_ batch
or a _list_ of batches. The batch also includes common pre-and post **run** tasks, which are common for each **run** but not for each **batch**.
_**TZ: keen to change the pre/post wording here to avoid confusion with pre-batch/post-batch**_.
* **pre-processing:** Common task(s) that are executed _before_ all **batch** execution.
* **post-processing:** Common task(s) that are executed _after_ all **batches** are completed.

Also note:

* **a job:** Once a run has been submitted to an HPC backend (such as SLURM) as part of a batch, we define it as a job. It is distinguished from a run,
as `model-ensembler` enables configuration that can control the number of jobs that are executed concurrently on an HPC cluster. This is independent from the run configuration, and follows the [SLURM naming convention](https://slurm.schedmd.com/quickstart.html). 

## Basic Usage

Under the `examples/` folder you will find example configs and templates that we can run on a local machine:

```shell
examples/
├── template_job/
│   ├── inputfile.j2
│   ├── preprocess.sh.j2
│   ├── slurm_run.sh.js
│   └── postprocess.sh.j2
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

## Where to go from here
The idea of `model-ensembler` is to give you the flexibility to set this up for your
own ensembles.

The basic pattern for using this toolkit is:

1. Adapt job/model run templates 
1. Adapt YAML Configuration
1. Running the job using `model_ensemble`
