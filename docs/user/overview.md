# Configuration & Templates Overview
Before we dive into an overview of how `model-ensembler` works, **Figure 1** provides a visual overview of how 
the configuration and templates interact to generate our ensemble.

![Definitions diagram, dark mode](../images/definitions.png#only-dark)
![Definitions diagram, light mode](../images/definitions.light.png#only-light)
/// caption
**Figure 1:** Visual overview of the definitions used throughout `model-ensembler` documentation. Boxes in green are edited by the user.
///

This overview will be expanded on in the [Building Configuration](yaml.md) and [Building Templates](templates.md) sections.
Before reading these, an overview of definitions used throughout the documentation:

* **a run:** A run refers to the execution of a model, with a given set of parameters. A run will be submitted to an HPC backed (such as SLURM).
* **a batch:** We refer to the collection of model runs as a batch. `model-ensembler` can be used to configure a _single_ batch
or a _list_ of batches. The batch also includes common pre-and post **batch** tasks, which are common for all **runs** but not for all **batches**,
as well as pre-and post **run** tasks which are unique for each **run**.
* **pre-processing:** Common task(s) that are executed _before_ all **batch** execution.
* **post-processing:** Common task(s) that are executed _after_ all **batches** are completed.

Also note, not pictured:

* **a job:** Once a run has been submitted to an HPC backend (such as SLURM) as part of a batch, we define it as a job. It is distinguished from a run,
as `model-ensembler` enables configuration that can control the number of jobs that are executed concurrently on an HPC cluster. This is independent from the run configuration, and follows the [SLURM naming convention](https://slurm.schedmd.com/quickstart.html). 

## Folder Structure
The configuration and templates are organised as in the `examples/` folder:

```shell
examples/
├── template_job/
│   ├── inputfile.j2
│   ├── pre_run.sh.j2
│   ├── slurm_run.sh.js
│   └── post_run.sh.j2
└── ensemble_config.yml
```