# Usage

## Definitions
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

## Basic Usage

There are some examples under "example" that can be run on a local machine (you 
can switch off slurm submission via the CLI `-s` switch)

The basic pattern for using this toolkit is

1. Create the execution environment (see previous section)
1. Adapt a job/model run
1. YAML Configuration
1. Running the job

### Adapt a job/model run

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

### YAML Configuration

To make up a set of runs we use a YAML configuration file which is clear to 
read and simple to manage. 

The idea is that you can define a batch, or set of batches, containing 
individual runs that are individually templated and run. These runs are done 
according to a common configuration defined for the batch.

The configuration is split up into the following sections: 

* `vars`: global configuration defaults
* `pre_process`/`post_process`: tasks to be run before any batches commence, or 
  after they've completed
* `batches`: a list of batches to be run concurrently

Each batch is then split into the following sections (**please note this is 
likely to be changed during development**): 

* configuration: there are numerous options that control how the batch operates
  * `name`: an identifier that's used as the prefix for the run ID
  * `templatedir`: directory that will be copied as run directories, can contain 
    both templates and symlinks
  * `templates`: a list of templates to be processed by Jinja (can be any text 
    file)
  * `job_file`: the file to be used to submit to SLURM
  * `cluster`/`basedir`/`email`/`nodes`/`ntasks`/`length`: job_file parameters 
    for SLURM
  * `maxruns`: the maximum amount of runs to be processing (pre_run, actual run 
    and post_run  activities) at once
  * `maxjobs`: the maximum amount of jobs to have running in the HPC at once
* `pre_batch`/`post_batch`: tasks to be run before or after the batch
* `pre_run`/`post_run`: tasks to be run prior to or after each run within the 
  batch

#### Tasks

There are numerous tasks that can be defined within the pre_ and post_ sections, 
which allow you to specify actions to take place throughout the execution 
lifetime. 

Tasks are either **checks**, which block until a condition is satisfied, or 
**processing**, which are activities that will do something and result in 
failure if not completed successfully.

* `jobs` (check): allows you to manually check that there aren't too many jobs 
  running in the HPC.  
* `submit` (processing): manually submit a task to the HPC backend - in 
  addition to the core submission specified by the configuration. 
* `quota` (check): allows you to check that you have enough user quota space 
  to progress.
* `check` (check): run a script that returns a success/failure error code. This 
  can be failure tolerant (check will be  repeated) or intolerant (failure 
  will cause the run to fail)
* `execute` (processing): run a script until completion
* `move` (processing): copy (using rsync) run directory contents to another 
  destination
* `remove` (processing): remove either the run directory or another (specified) 
  directory

#### Variables

Variables are available in templates with increasing, overridden, granularity. 
Defaults are specified from `vars` at the top level and then the `run` 
dictionaries, in addition to the batch level configurations, are all available 
within the templates.  

### Running the job / CLI reference

```
usage: model_ensemble [-h] [-n] [-v] [-c] [-s] [-p] [-k SKIPS] [-i INDEXES]
                   [-ct CHECK_TIMEOUT] [-st SUBMIT_TIMEOUT]
                   [-rt RUNNING_TIMEOUT] [-et ERROR_TIMEOUT]
                   configuration
```