# Technical Overview
Firstly, detailed documentation generated from the docstrings are available
under `API/`. 

This page intends to give a technical overview beyond the `API/`, of how different components of `model-ensembler`
work together, and provide accompanying notes to aid developers. It is not intended to be read from start to finish.

## cli
`cli.py` provides the main CLI entrypoint (the "Model Ensemble Runner"), and parses various arguments to control it. 

## Configuration JSON schema: `config.py` and `model-ensemble.json`
`model-ensemble.json` defines the schema which a configuration should follow. `config.py` will use this to
validate the configuration file it is given.

`config.py`:

* Contains `YAMLConfig` class which validates the yaml file against `model-ensemble.json` schema.
* Contains `Task` and `TaskArrayMixin`, `Task` obtains tasks from `TaskSpec` in `YAMLConfig`, stores Tasks
as an array. `TaskArrayMixin` obtains tasks from batch object members.
* Contains `EnsembleConfig` class, represents ensemble (collects `YAMLConfig` and `TaskArrayMixin`)
* Contains `Batch` class, represent batch (collects `BatchSpec` and `TaskArrayMixin`)

## Batcher
Contains execution core code.

Contains `BatchExecutor` class, which monitors all runs independent of one another, but batch has to complete in full.
Can control submission rate into SLURM.

Note:

* It relies on host porcessor staying alive.
* It relies on workflow picking itself up.
* It is not aware of state.


## Runners

Core execution functions for the batcher.

## cluster
Contains backend-specific code (`slurm.py`, `dummy.py`)

## tasks

`exceptions.py`
`hpc.py`
`sys.py` defines processing tasks
`utils.py` execute command handling

## templates

## utils
