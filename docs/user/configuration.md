# Building Configuration

To make up a set of runs we use a YAML configuration file which is clear to 
read and simple to manage. 

The idea is that you can define a batch, or list of batches, containing 
individual runs that are individually templated and run. These runs are done 
according to a common configuration defined for the batch.


## Structure
The configuration is split up into the following sections: 

* `vars`: global configuration defaults.
* `pre_process`/`post_process`: tasks to be run before any batches commence, or 
  after they've completed.
* `batch_config:` configuration controlling how all batches are executed.
* `batches`: a list of batches to be run concurrently.

This leads to the following structure for an `ensemble_config.yaml`:

```yaml
ensemble:
  vars: []
  pre_process: []
  post_process: []
  batch_config: []
  batches: []
```

## Tasks
There are tasks that can be defined within `pre_process` and `post_process` sections, 
which allow you to specify actions to take place throughout the execution lifetime. 

Tasks are either:

  1. **checks**, which block execution until a condition is satisfied, or;
  1. **processing**, which are activities that will _do_ something and result in 
    failure if not completed successfully.

Below are the different tasks you can specify:

* `jobs` (check): allows you to manually check that there aren't too many jobs 
  running in the HPC.  
* `quota` (check): allows you to check that you have enough user quota space 
  to progress.
* `check` (check): run a script that returns a success/failure error code. This 
  can be failure tolerant (check will be  repeated) or intolerant (failure 
  will cause the run to fail).
* `submit` (processing): manually submit a task to the HPC backend - in 
  addition to the core submission specified by the configuration. 
* `execute` (processing): run a script until completion.
* `move` (processing): copy (using rsync) run directory contents to another 
  destination.
* `remove` (processing): remove either the run directory or another (specified) 
  directory.

## Configuration Sections
### Variables

Variables are available in templates with increasing, overridden, granularity. 
Defaults are specified from `vars` at the top level and then the `run` 
dictionaries, in addition to the batch level configurations, are all available 
within the templates.  

```yaml
  vars:
    configuration: test.yaml
```

### Pre-process
Contains **tasks** to be run before any batches commences.

In this example, an `execute` tasks with a command (`cmd`) to create two files, `process.touch` and `process.keep`:

```yaml
  pre_process: 
  - name:   execute
    args:
      cmd:  touch process.touch process.keep
```

### Post-process
Contains **tasks** to be run after all batches are completed.

In this example, an `execute` command which removes `process.touch` created in the pre-process:
```yaml
  post_process:
  - name:   execute
    args:
      cmd:  rm process.touch
```

### Batch Configuration
The `batch_config` controls how a batch is executed and submitted to an HPC backed.

There are numerous `batch_config` options that control this:

  * `templates`: a list of templates to be processed by Jinja (can be any text file).
  * `job_file`: the file to be used to submit to SLURM.
  * `cluster`/`basedir`/`email`/`nodes`/`ntasks`/`length`: job_file parameters for SLURM.
  * `maxruns`: the maximum amount of runs to be processing (pre_run, actual run and post_run  activities) at once.
  * `maxjobs`: the maximum amount of jobs to have running in the HPC at once.

```yaml
  batch_config:
    templates:
    - inputfile.j2
    - pre_run_.sh.j2
    - slurm_run.sh.j2
    - post_run_.sh.j2
    job_file:     slurm_run.sh
    cluster:      short
    email:        test@example.org
    nodes:        1
    ntasks:       8
    length:       00:20:00
    maxruns:      8
    maxjobs:      2
```

### Batches
Each of the `batches` is then split into the following sections: 

  * `name`: an identifier that's used as the prefix for the run ID.
  * `templatedir`: directory that will be copied as run directories, can contain both templates and symlinks.
  * `basedir`:
  * `pre_batch`/`post_batch`: **tasks** to be run before or after the batch.
  * `pre_run`/`post_run`: **tasks** to be run prior to or after each run within the batch.
  * `runs`: a list of runs, each with their own `custom_id`.

```yaml
  batches:
    - name:         tst1
      templatedir:  ../template_job
      basedir:      ./tst1
      pre_batch:    
      - name:   check
        args:
          cmd:  test -f batch.ready
      - name:   execute
        args:
          cmd:  mkdir -p datadir
      - name:   execute
        args:
          cmd:  touch pre_batch.keep
      pre_run:      
      - name:   execute
        args:
          cmd:  ./pre_run.sh
          log:  True
      - name:   check
        args:
          cmd:  test -d ../datadir
      - name:   execute
        args:
          cmd:  pre_run.keep
      runs:         
      - custom_id:  1
      - custom_id:  2
      - custom_id:  3
      - custom_id:  4
      post_run:     
      - name:   execute
        args:
          cmd:  ./post_run.sh
      - name:   execute
        args:
          cmd:  touch post_run.keep
      post_batch:
      - name:   execute
        args:
          cmd:  rmdir datadir
      - name:   execute
        args:
          cmd:  touch post_batch.keep
```

The batches are defined, and the scripts generated from the files in `template_job/` are executed.

!!! note "Individual batch configuration"
    Should you wish to individually configure batches, it is possible to use
    `batch_config:` options under `batches:`, for example:

    ``` yaml
      batches:
    - name:         tst1
      templatedir:  ../template_job
      templates:
      - inputfile.j2
      - pre_run_.sh.j2
      - slurm_run.sh.j2
      - post_run_.sh.j2
      job_file:     slurm_run.sh
      cluster:      short
      basedir:      ./tst1
      email:        test@example.org
      nodes:        1
      ntasks:       8
      length:       00:20:00
      maxruns:      8
      maxjobs:      2
    ```

    **Note on hierarchy of variables**

Now that you are familiar with the configuration, we will cover building templates
in the [next section](templates.md).