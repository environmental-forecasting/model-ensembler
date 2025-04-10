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


## Adapt a job/model run

The core component of any slurm_batch run is a working cluster job. If not 
designing from scratch, think about the following in order to adapt the job 
to a batch configuration:

* What source data/processing do you need before the whole batch and how do you 
  get/do it
* What source data/processing do you need before each run and how do you get/do 
  it
* What checks are needed before each run is submitted to slurm
* What needs to change in the job for each run
* What happens afterwards: what needs checking, where is the data going, what 
  cleanup is required

Breaking each activity down should allow you to consider what pre and post 
processing you need to implement AS SINGLE ACTIVITIES. 

Quite a common issue with jobs is that people have a monolithic script doing 
everything that doesn't lend itself to batching. This monolith should be 
broken down into activities that can be templated out (to provide per-run 
variance) and individually assessed prior to moving on. 

These activities are then all stitched together with the configuration.