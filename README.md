# SLURM Toolkit

## Introduction

## Installation

pyslurm needs to be installed from source, it seems they're not packaging it.

```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Install from source pyslurm ref. 19.05.00

```
git clone git@github.com:PySlurm/pyslurm.git <dest>
cd <dest>
git checkout 19.05.0
pip install <dest>
```

## Basic Usage

TODO

## Contributing

This program is under extreme development and is likely to be mostly rewritten, as it's gone from one-off tool to potentially reusable. If you want to contribute I suggest getting in touch with the maintainers first, as the task-plugin architecture will definitely be redesigned, as likely will be the execution interface.

The configuration for batching is likely to remain in a "similar" state. But hey, I'm not offering any guarantees ;-)

## Further documentation

Wherever this repository is, there should be a WIKI also. This will go into further details about the configuration structure and operation. 

