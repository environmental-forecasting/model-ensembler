# Building Configuration & Templates

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