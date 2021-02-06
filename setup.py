import setuptools

from setuptools import dist, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="model-ensembler",
    version="0.4.0",
    author="James Byrne",
    author_email="jambyr@bas.ac.uk",
    description="Model Ensemble for batch workflows on HPCs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.github.com/JimCircadian/model-ensembler",
    packages=setuptools.find_packages(),
    keywords='slurm, hpc, tools, batch, model, ensemble',
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
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
