# Technical Notes
Firstly, detailed documentation generated from the docstrings are available under `API/`. 

This page intends to give technical notes beyond the `API/`, of how different components of `model-ensembler`
work together, and provide accompanying notes to aid developers. It is not intended to be read from start to finish.

## model_ensembler
### batcher
Contains execution core code.

Contains `BatchExecutor` class, which monitors all runs independent of one and executes batches based on the configuration. Can control submission rate into SLURM.

Note:

* It relies on host porcessor staying alive.
* It relies on workflow picking itself up.
* It is not aware of state.

### cli
`cli.py` provides the main CLI entrypoint (the `model_ensemble` command), and parses various arguments to control it.

`model_ensemble` calls the `BatchExecutor`, which is fed the configuration and backend options through the
parsed arguments.

### config
`model-ensemble.json` defines the schema which a configuration should follow.

`config.py` will use this to validate the configuration file it is given.

`config.py`:

* Contains `YAMLConfig` class which validates the yaml file against `model-ensemble.json` schema.
* Contains `Task` and `TaskArrayMixin`, `Task` obtains tasks from `TaskSpec` in `YAMLConfig`, stores Tasks
as an array. `TaskArrayMixin` obtains tasks from batch object members.
* Contains `EnsembleConfig` class, represents ensemble (collects `YAMLConfig` and `TaskArrayMixin`)
* Contains `Batch` class, represent batch (collects `BatchSpec` and `TaskArrayMixin`)

### exceptions
Contains a `TemplatingError` exception. Other exceptions are handled in `tasks/exception.py`.

### runners
Core execution functions for the batcher, for example functionality to asynchronously run a list of tasks.

### templates
Contains the functionality to render batch templates and preparing directories for their transfer to run directories. 

### utils
Contains general purpose functionality, such as arguments handling and logging.

## tasks
Submodule which contains _generic_ tasks, utilities and exceptions:

* `exceptions.py`: contains exceptions which relate to the tasks (e.g. * `ProcessingException` for processing failures)
* `hpc.py`: contains HPC-related tasks methods, such as checking the number of SLURM jobs.
* `sys.py` contains all methods for system related tasks, such as 
rsyncing directory contents.
* `utils.py`: contains general implementation and functionality related to tasks.

## cluster
Submodule which contains backend-specific functionality, currently SLURM and local (`slurm.py`, `dummy.py`).