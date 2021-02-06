import setuptools

from setuptools import dist, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

dist.Distribution().fetch_build_eggs(['Cython'])

setup(
    name="model-ensembler",
    version="0.4.0a4",
    author="James Byrne",
    author_email="jambyr@bas.ac.uk",
    description="Model Ensemble for batch workflows on HPCs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jimcircadian/meg",
    packages=setuptools.find_packages(),
    keywords='slurm, hpc, tools, batch, model, ensemble',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    entry_points={
        'console_scripts': [
            'model_ensemble=model_ensembler.cli:main',
        ],
    },
    python_requires='>=3.6, <4',
    install_requires=[
        "Cython",
        "Fabric",
        "jinja2",
        "jsonschema",
        # TODO: Why are they not packaging this any more? 
        # TODO: This isn't a strong dependency for what we do, maybe break it off...
        #"pyslurm==19.5.0.0",
        "pyyaml",
    ],
    include_package_data=True,
)
