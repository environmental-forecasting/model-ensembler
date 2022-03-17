# Model Ensembler

## Introduction

This is a tool to assist users in running model ensembles on HPCs, potentially 
in conjunction with other external systems. It will be easy to be extend for 
various other HPC backends (currently just SLURM is supported), as well as 
being easy to extend code wise for new tasks that support the ensemble 
workflows.

## Installation

Refit the instructions to match however you like created virtual 
environments! Python3.8 is the development Python I'm currently using but 
anything above that is likely to work, as well as possibly 3.7, but 3.6 won't. 

```
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install model-ensembler
```

### Checking it works

You can run the sanity checker with the following command, choosing either 
the dummy executor or slurm as appropriate.

**TODO: v0.5.4: in the meantime you can run the examples**

```
model_ensemble_check [dummy|slurm]
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

## Testimonials

Some lovely folk in the British Antarctic Survey have provided testimonials 
describing their use of the ensembler...

__Clare Allen, running significant WRF batches, original motivator 
for the tool__

```
The model-ensembler is a fantastic tool that saves time, reduces stress and 
significantly decreases the chance of human error when running many model 
configurations.

The model-ensembler was invaluable for my work as a postdoc at BAS while I was 
investigating many (Weather Research and Forecasting) WRF model configurations. 
The model parameters I wanted to change were stated in a file in a simple and 
intuitive format along with my model running requirements such as number of 
nodes to run the model. The model-ensembler only needed to be submitted once, 
and it would only submit the model runs after checking that there was enough 
space for the model data and that I had not exceeded my fair usage at that 
moment while using the academic supercomputer. Once a model run had completed, 
the model-ensembler automatically transferred the data to an archive space, 
freeing up space for the next model run. Altogether, this saved me a 
considerable amount of time, at least 1 hour per run, if not more, and this 
soon mounts up when you are submitting tens and hundreds of individual model 
runs. I did not have to set up each model directory, or model setup files. I 
did not have to check for space, nor submit each model run separately. Nor did 
I have to check or worry about space running out. As this is fully automated, 
there was much less chance that I would make a mistake and modify the model 
setup in an unintended way. Using the model-ensembler tool freed up my time, and 
enabled to focus more on the science without being interrupted due to the need 
to set more runs going. The model-ensembler tool is very versatile and can be 
utilised by many models or other computational processes (for example plotting 
a lot of data). The model-ensembler is an exceptional tool and I recommend to 
anyone who needs to submit batches of model runs.
```

__Rosie Williams, using for [WAVI][5] workflow executions__

```
  I'd say that it would take maybe one day to get an ensemble of 100 WAVI 
  runs up and running, and less than an hour with the model ensembler. Then 
  the resubmitting and monitoring of jobs would have taken up human time and 
  led to down time, when jobs that had timed out were not resubmitted.... 
  it's hard to estimate. Maybe if it was say one month of running time per 100 
  jobs,  with them all running nicely the whole time in the model ensembler, 
  that might have ended up taking an extra week maybe if the jobs had to be 
  monitored and resubmitted manually (especially if they needed resubmitting 
  on Friday nights!)... It's hard to put a number on how much time it saves. 
  It certainly saves a lot of frustrating and tedium too.....!

  In terms of human hours. With model ensembler: 1h set up, minimal monitoring. 
  Max 1h/week checking everything is running. 3-5 hours maximum total. Without 
  model-ensembler: 8h set up, 2-3 hours for 5 weeks checking and 
  resubmitting jobs: approx 18-25 hours.

  With the manual method, running say 1000 runs would be really horrible. 
  With the ensembler, it'd be easy.
```

__Tom Andersson, used for [IceNet][6] drop and relearn parameter analysis__

```
  In terms of the drop-and-relearn experiment it would comprise about 2,000 
  individual training runs, assuming we use 5 random seeds per run. Assuming 
  it's 1 hour per training run (which I can't remember exactly but is the 
  right order of magnitude) that's a bit over 2 months to compelte with no 
  model ensembler parallelisation.

  It would also have be be finickily set up with SLURM to stop the single job 
  after N runs and resubmit or something. All that bespoke stuff could have 
  taken me 2 weeks or so to get my head around. With the parallelisation of 
  the model ensembler, say 4 job running at a time, we'd get the run-time 
  down to 2 weeks, as well as removing the overhead of me having to fiddle 
  around with submitting the SLURM jobs, which isn't my area of expertise.

  So around 2.5 months to around 2 weeks
```

## Future plans

Current plans are captured now in the github issues. There's nothing in the 
long term that I'm focusing on for this tool, except to maintain it and see 
if I can promote the usage a bit more. 

This tool was merely to help out with a single support ticket for a weather 
model run, but the concept had potential and it was easier than deploying 
something more substantial! If there are better approaches or tools that do 
something similar, very keen to look at them! 

Certainly, things like Airflow and job arrays have similar concepts, but are 
either more heavyweight/less suitable deployment wise or not abstracted enough 
for simplifying lives, respectively!!!

### Cycl

Recently we noticed at Cycl [4], so in the medium term it's worth evaluating this 
tool and compare it to model\_ensembler, as it seems pretty lightweight (which
is the reason many others are a pain to use) and could be a good tool to use in 
place. model\_ensembler is just quick and easy, so moving to a decent graph based
workflow executor is preferable if you're thinking of long term implementation and
education. 

## Further documentation

Wherever this repository is, there should be a WIKI also. This will go into 
further details about the configuration structure and operation.

## Copyright

[MIT LICENSE](LICENSE)

&copy; British Antarctic Survey 2021 
 
[1]: https://github.com/wrf-model/WRF
[2]: https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google
[3]: https://github.com/antarctica/IceNet-Pipeline
[4]: https://cylc.github.io/
[5]: https://github.com/RJArthern/WAVI.jl
[6]: https://www.nature.com/articles/s41467-021-25257-4
