## Building Templates
In this section we will be focusing on the [jinja2](https://jinja.palletsprojects.com/en/stable/) templates under `template_job/`.

These templates will be stitched together with the configuration, which is covered in the [next section](yaml.md).

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
`inputfile.j2`:
```j2
This is {{ run.custom_id }}
```

### Pre-process
`preprocess.sh.j2`:
```j2
#!/usr/bin/env bash

echo "PRE PROCESSING: {{ run.cluster }} `cat inputfile`"

SLEEP_SECS=`expr $RANDOM / 3000`
echo "Sleeping for $SLEEP_SECS"
sleep $SLEEP_SECS
```

### Slurm Run
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

The core component of any slurm_batch run is a working cluster job. If not 
designing from scratch, think about the following in order to adapt the job 
to a batch configuration:

### Post-process
`postprocess.sh.j2`:
```j2
#!/usr/bin/env bash

echo "POST PROCESSING: `cat inputfile`"

SLEEP_SECS=`expr $RANDOM / 3000`
echo "Sleeping for $SLEEP_SECS"
sleep $SLEEP_SECS

```


