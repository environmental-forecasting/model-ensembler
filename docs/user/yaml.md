# YAML Configuration

To make up a set of runs we use a YAML configuration file which is clear to 
read and simple to manage. 

The idea is that you can define a batch, or list of batches, containing 
individual runs that are individually templated and run. These runs are done 
according to a common configuration defined for the batch.

The configuration is split up into the following sections: 

* `vars`: global configuration defaults
* `pre_process`/`post_process`: tasks to be run before any batches commence, or 
  after they've completed
* `batches`: a list of batches to be run concurrently

Each batch is then split into the following sections (**please note this is 
likely to be changed during development**): 

* `configuration`: there are numerous options that control how the batch operates
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

## Tasks

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

## Variables

Variables are available in templates with increasing, overridden, granularity. 
Defaults are specified from `vars` at the top level and then the `run` 
dictionaries, in addition to the batch level configurations, are all available 
within the templates.  
