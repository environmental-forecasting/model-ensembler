# Contributing to model-ensembler
Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

Please note that this project is released
with a [Contributor Code of Conduct](code_of_conduct.md).

## Types of Contributions

You can contribute in many ways:

### Open an Issue
Open an issue on [Github](https://github.com/antarctica/model-ensembler/issues).

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs
Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features
Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation
The `model-ensembler` documentation can always be improved, whether as part of the
official docs, in docstrings, or even on the web in blog posts, articles, and such. Refer to the [Documentation Guidelines](#documentation-guidelines) below for guidance on how to contribute to the docs.

### Submit Feedback
The best way to send feedback is to [open an issue](https://github.com/antarctica/model-ensembler/issues).

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome.

## Development Guidelines
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
python setup.py develop # Does not work currently, this will change
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
    This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Please refer to the [change log](CHANGELOG.md) for the latest version and instructions on how to increment the version for your changes. If in doubt, do not hesitate to clarify this with the maintainers in your corresponding issue.

8\. Commit your changes and push your branch to GitHub:

```shell
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

9\. Submit a pull request through the GitHub website.

!!! note "Pull Request Guidelines"

    Before you submit a Pull Request (PR), check that it meets these guidelines:

    1. The title of your PR should contain a version number and briefly describe the change,
    for example: **v0.5.7 fixing bug in cli.py**.
    1. The body of your PR should contain `Fixes #issue-number`.
    1. The pull request should include tests and pass them, where appropriate.
    1. If the pull request adds functionality, the documentation should be updated accordingly.
    Please see the next section for a detailed breakdown of how to contribute to the docs.

## Documentation Guidelines

The documentation is built using [mkdocs](https://www.mkdocs.org/). We use [mkdocstrings](https://mkdocstrings.github.io/) and [mkdocs-autoapi](https://mkdocs-autoapi.readthedocs.io/en/latest/) to automatically generate the API references.

### Installing Dependencies
To install the documentation dependencies:

```bash
source venv/bin/activate

# Temporary, move all of this to pyproject.toml?
pip install -r docs/requirements.txt
```

### Building the Docs
To preview the documentation locally:
```bash
mkdocs serve
```

To build the documentation:
```bash
mkdocs build
```

### Navigation
The navigation is handled in `mkdocs.yml`:
```yaml
nav:
  - Installation: installation.md
  - Usage: usage.md
  - Contributing: contributing.md
  - Acknowledgements: acknowledgements.md
  - Testimonials: testimonials.md
  - News: news.md
```
The pages listed here can be edited manually.

Note that the API section (which is not listed under `nav:`) is automatically generated using `mkdocstrings` and `mkdocs-autoapi`, when you call `mkdocs serve`.

This is because we use the following configuration in `mkdocs.yml`:
```yaml
plugins:
  - search
  - mkdocs-autoapi:
      autoapi_add_nav_entry: API
  - mkdocstrings:
      handlers:
        python:
          paths:
            - .
          options:
            show_submodules: true
            docstring_style: google
            heading_level: 3
```

Therefore, there is no need to create or edit `.md` files when you make a change to the code under `model_ensembler/`. Do make sure you update the docstrings if needed.

### Docstrings Style
For the docstrings, please follow the [Google Style Guide][4]. For more information on `mkdocstrings`, see their [Docstring Options][5].

### Diagrams
Explanatory diagrams are provided throughout the documentation. These are built using [drawio](https://www.drawio.com/).
If documentation diagrams require updating, their original `.drawio` files can be found under `docs/images/drawio`.

[1]: https://github.com/wrf-model/WRF
[2]: https://github.com/RJArthern/WAVI.jl
[3]: https://github.com/antarctica/IceNet-Pipeline
[4]: https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google
[5]: https://mkdocstrings.github.io/python/usage/configuration/docstrings/
