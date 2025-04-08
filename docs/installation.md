# Installation
Refit the instructions to match however you like created virtual 
environments! Python3.8 is the development Python I'm currently using but 
anything above that is likely to work, as well as possibly 3.7, but 3.6 won't. 

```
python3.8 -m venv venv
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