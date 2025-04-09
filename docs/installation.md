# Installation
To install `model-ensembler`:

```
python -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install model-ensembler
```
## Checking it works

You can run the sanity checker with the following command, choosing either 
the dummy executor or slurm as appropriate.

**TODO: v0.5.4: in the meantime you can run the examples**

```
model_ensemble_check [dummy|slurm]
```