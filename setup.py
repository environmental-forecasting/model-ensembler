from setuptools import setup, find_packages

"""Setup module for model_ensembler

"""

from model_ensembler import __author__, __email__, __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="model-ensembler",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="Model Ensembler for managed batch workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.github.com/jimcircadian/model-ensembler",
    project_urls={
        "Bug Tracker": "https://github.com/jimcircadian/model-ensembler/issues",
    },
    packages=find_packages(),
    keywords='slurm, hpc, tools, batch, model, ensemble, local',
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Development Status :: 3 - Alpha",
        "Topic :: System :: Distributed Computing",
    ],
    entry_points={
        'console_scripts': [
            'model_ensemble=model_ensembler.cli:main',
        ],
    },
    python_requires='>=3.7, <4',
    install_requires=[
        "jinja2",
        "jsonschema",
        "pyyaml",
    ],
    include_package_data=True,
)
