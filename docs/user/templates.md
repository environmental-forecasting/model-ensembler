## Building Templates
In this section we will be focusing on the [jinja2](https://jinja.palletsprojects.com/en/stable/) templates under `template_job/`.

These templates are stitched together with the configuration, covered in the [previous section](configuration.md).

### Before starting
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
Your model will require input data.

For the purposes of running an example, the "data" in `inputfile.j2` is a 
custom string:

`inputfile.j2`:
```j2
This is {{ run.custom_id }}
```

### Pre-run
Before running your model, you will likely need to do perform some data wrangling or processing.

For the purpose of our example, `pre_run.sh.js` simply takes `inputfile`'s string above,
prints it and executes a random `sleep`:

`pre_run.sh.j2`:
```j2
#!/usr/bin/env bash

echo "PRE PROCESSING: {{ run.cluster }} `cat inputfile`"

SLEEP_SECS=`expr $RANDOM / 3000`
echo "Sleeping for $SLEEP_SECS"
sleep $SLEEP_SECS
```

### Slurm Run
The `slurm_run.sh.j2` template is an example of a script that would be executed
under `runs:` and sent to an HPC backend, in this case SLURM. `SBATCH` headers
are provided to parse in the `batch_config:` parameters. Other run configuration
is also parsed (e.g. `{{ run.configuration}}`):

`slurm_run.sh.j2`:
```j2
#!/bin/bash
#
# Output directory
#SBATCH --mail-type=begin,end,fail,requeue
#SBATCH --time={{ run.length }}
#SBATCH --job-name={{ run.name }}{{ run.custom_id }}
#SBATCH --nodes={{ run.nodes }}
#SBATCH --ntasks-per-node {{ run.ntasks }}
#SBATCH --ntasks-per-core 1
#SBATCH --mem=20gb
#SBATCH --partition={{ run.cluster }}
#SBATCH --account={{ run.cluster }}

# Now run some programs.

echo "Initiating from {{ run.configuration }}"

cd {{ run.dir }}

echo "Running in $PWD"

SLEEP_SECS=`expr $RANDOM / 1000`
echo "Sleeping for $SLEEP_SECS"
sleep $SLEEP_SECS

NUM="`cat inputfile`"
echo "Done with run number $NUM"
```

### Post-run
Finally, `post_run.sh.j2` would be executed after the run is completed.

A similar example as `pre_run.sh.j2` is provided:

`post_run.sh.j2`:
```j2
#!/usr/bin/env bash

echo "POST PROCESSING: `cat inputfile`"

SLEEP_SECS=`expr $RANDOM / 3000`
echo "Sleeping for $SLEEP_SECS"
sleep $SLEEP_SECS
```

!!! note "Building your own templates"
    When building your own templates, keep in mind:
    
    * Templates can be any type of script (not just `.sh`).
    * While `pre_run`, `run` and `post_run` are used as examples here
    to align with the config naming (`pre_run:`, `runs:`, `post_run:`),
    you can build more than one template for `pre_run:` and `post_run:`
    and execute them in order.



