# Model Ensembler

## Introduction

This is a tool to assist users in running model ensembles on HPCs, potentially 
in conjunction with other external systems. It will be easy to be extend for 
various other HPC backends (currently just SLURM is supported), as well as 
being easy to extend code wise for new tasks that support the ensemble 
workflows.

## Installation

Refit the instructions to match however you like created virtual 
environments! Python3.6 is the development Python I'm currently using but 
anything above that is likely to work, with below that not guaranteed. 

```
python3.6 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install model-ensembler
```

### Checking it works

This runs a nice little test job in the examples directory of the source. It 
doesn't need slurm, you use the `-s` option to avoid the actual submission.

```
git clone https://github.com/JimCircadian/model-ensembler.git
cd model-ensembler/examples/
model_ensemble -s sanity-check.yml
```


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

## Contributing

This program is still under development and is in its infancy, though it's 
progressed from a one-off tool to reusable (at the British Antarctic Survey 
it's been used for running [WRF][1] ensembles numerous times and will help 
power future [IceNet][3] and Digital Twin pipeline.) 

Contributions now this is in the public domain are welcome!

I'm now trying to keep to the [Google Style Guide][2] for documentation

## Future plans

There are a few items on the list: 

* multiple batches can be specific and run, but some of the CLI switches 
  aren't suitable for multi-batch ensembles (indexes/skips)
* sort out a proper context hierarchy for variable injection into the 
  templates/runs
* ensure the slurm specific functionality is detached from the generic 
  execution model 
* add another HPC backend (e.g. PBS/dummy)
* add a test suite and make it a properly maintained package now it's in the 
  public domain
* better documentation and examples
* add sanity check as CLI operation

This tool was merely to help out with a single support ticket for a weather 
model run, but the concept had potential and it was easier than deploying 
something more substantial! If there are better approaches or tools that do 
something similar, very keen to look at them! 

Certainly, things like Airflow and job arrays have similar concepts, but are 
either more heavyweight/less suitable deployment wise or not abstracted enough 
for simplifying lives, respectively!!!

## Further documentation

Wherever this repository is, there should be a WIKI also. This will go into 
further details about the configuration structure and operation.

## Copyright

[MIT LICENSE](LICENSE)

&copy; British Antarctic Survey 2021 
 
[1]: https://github.com/wrf-model/WRF
[2]: https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google
[3]: https://github.com/antarctica/IceNet-Pipeline