# Contributing
This program is still under development and is in its infancy, though it's 
progressed from a one-off tool to reusable (at the British Antarctic Survey 
it's been used for running [WRF][1] and WAVI[2] ensembles and will help 
power future [IceNet][3] and Digital Twin pipeline.) 

Contributions now this is in the public domain are welcome!

## Installing for Development

## Building Documentation

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

[1]: https://github.com/wrf-model/WRF
[2]: https://github.com/RJArthern/WAVI.jl
[3]: https://github.com/antarctica/IceNet-Pipeline
[4]: https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google
[5]: https://mkdocstrings.github.io/python/usage/configuration/docstrings/
