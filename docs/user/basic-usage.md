# Usage
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
