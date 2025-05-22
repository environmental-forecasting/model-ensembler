# Software Development Guide
To start working on `model-ensembler` locally, please follow these steps:

1. Fork the `model-ensembler` repo [on GitHub](https://github.com/environmental-forecasting/model-ensembler).
2. Clone your fork locally:

```shell
git clone git@github.com:your_name_here/model-ensembler.git
```

3\. Install your local copy into a virtualenv:

```shell
cd model-ensembler/
python -m venv venv

# Editable installation, including all optional dependencies
pip install -e .[tests, lint, docs]
```

4\. Create a branch for local development:

```
git checkout -b name-of-your-bugfix-or-feature
```

Now you can make your changes locally.

5\. For bigger changes, it is a good idea to _first_
[open an issue](https://github.com/environmental-forecasting/model-ensembler/issues),
and make sure a team agrees it is needed and within scope.

6\. When you're done making changes, check that your changes comply with [flake8](https://flake8.pycqa.org/en/latest/) code styling, pass the tests and that you can build the documentation successfully:

```shell
flake8 model-ensembler

pytest

mkdocs build
```

7\. Add your changes to `docs/changelog.md`.

!!! Note "Semantic Versioning"
    This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Please refer to the [change log](/docs/change_log.md) for the latest version and instructions on how to increment the version for your changes in `__init__.py`.
    
    The version number from `__init__.py` is automatically propagated to `pyproject.toml`.
    
    If in doubt, do not hesitate to clarify this with the maintainers in your corresponding issue.

If you have introduced any dependencies or executable scripts, make sure to add them under the appropriate headers in `pyproject.toml`. Check the package still builds successfully:

```shell
python -m build 
```

8\. Commit your changes and push your branch to GitHub:

```shell
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

9\. Submit a pull request against the [main branch on GitHub](https://github.com/environmental-forecasting/model-ensembler/tree/main).

!!! note "Pull Request Guidelines"

    Before you submit a Pull Request (PR), check that it meets these guidelines:

    1. The title of your PR should contain a version number and briefly describe the change,
    for example: **v0.5.7 fixing bug in cli.py**.
    1. The body of your PR should contain `Fixes #issue-number`.
    1. The pull request should include tests and pass them, where appropriate.
    1. If the pull request adds functionality, the documentation should be updated accordingly.
    Please see the next section for a detailed breakdown of how to contribute to the docs.
