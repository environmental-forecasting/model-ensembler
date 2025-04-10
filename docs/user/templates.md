# Building Configuration & Templates
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

## Folder Structure
A reminder of the `examples/` folder structure:

```shell
examples/
├── template_job/
│   ├── inputfile.j2
│   ├── preprocess.sh.j2
│   ├── slurm_run.sh.js
│   └── postprocess.sh.j2
└── ensemble_config.yml
```

In this section we will be focusing on the [jinja2](https://jinja.palletsprojects.com/en/stable/) templates under `template_job/`.

These templates will be stitched together with the configuration, which is covered in the [next section](yaml.md).

## Adapting templates for your ensemble

Process diagram:

Considerations before adapting templates:

* What source data do you need for the whole batch and how do you ingest it?
* What processing tasks do you need to execute for all batches?
* What source data and processing tasks do you need to execute before all runs **within** each batch?  
* What checks are needed before each run is submitted to SLURM?
* What processing tasks do you need to execute when all runs **within** a batch are completed?
* What processing tasks do you need to executre when all **batches** are completed
(quality control checks, data transfer, directory cleanup).

Breaking each activity down should allow you to consider what pre-and post 
processing you need to implement as **single** activities. 

A common issue with modelling scripts, prior to considering ensembling, is having a monolithic script
which executes all of the above in one go. This does not lend itself to batching.
This monolith should be broken down into activities that can be templated out and
individually assessed prior to moving on. 

## Template Examples
### Input

### Pre-process

### Slurm Run

The core component of any slurm_batch run is a working cluster job. If not 
designing from scratch, think about the following in order to adapt the job 
to a batch configuration:



### Post-process



