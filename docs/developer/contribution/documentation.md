# Documentation Guide

The documentation is built using [mkdocs](https://www.mkdocs.org/). We use [mkdocstrings](https://mkdocstrings.github.io/) and [mkdocs-autoapi](https://mkdocs-autoapi.readthedocs.io/en/latest/) to automatically generate the API references.

### Installing Dependencies
To install the documentation dependencies:

```bash
source venv/bin/activate

pip install -e .[docs]
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
  - Overview: index.md
  - User Guide:
    - Configuration & Templates Overview: user/overview.md
    - Building Configuration: user/configuration.md
    - Building Templates: user/templates.md
    - Simple Example - WAVI: user/WAVI_example.md
  - Developer Guide:
    - Contribution:
      - Contributing: developer/contribution/contributing.md
      - Software Guide: developer/contribution/software.md
      - Documentation Guide: developer/contribution/documentation.md
      - Code of Conduct: developer/contribution/code_of_conduct.md
    - Functionality:
      - Technical Overview: developer/functionality/technical.md
  - Testimonials: testimonials.md
  - Change Log: change_log.md
  - Acknowledgements: acknowledgements.md
  - LICENSE: license.md
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
For the docstrings, please follow the [Google Style Guide][1]. For more information on `mkdocstrings`, see their [Docstring Options][2].

### Diagrams
Explanatory diagrams are provided throughout the documentation. These are built using [drawio](https://www.drawio.com/).
If documentation diagrams require updating, their original `.drawio` files can be found under `docs/images/drawio`.

[1]: https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google
[2]: https://mkdocstrings.github.io/python/usage/configuration/docstrings/
