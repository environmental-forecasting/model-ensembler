

```bash
├── templates/
│   ├── inputfile.j2
│   ├── pre_run.sh.j2
│   ├── slurm_run.sh.js
│   └── post_run.sh.j2
└── ensemble_config.yml
```

```yaml
ensemble:
    vars: []
    pre_process: []
    post_process: []

    batch_config:
        templates:
        - inputfile.j2
        - pre_run.sh.j2
        - slurm_run.sh.j2
        - post_run.sh.j2
        cluster: []
        nodes: []
        ntasks: []

    batches:
        - name: batch_1
          pre_run: []
          runs:
            - custom_id: 1
            - custom_id: 2
          post_run: []
        - name: batch_2
          pre_run: []
          runs:
            - custom_id: 1
            - custom_id: 2
          post_run: []
```