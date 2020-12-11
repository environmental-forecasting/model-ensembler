import setuptools

from setuptools import dist, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

dist.Distribution().fetch_build_eggs(['Cython'])

setup(
    name="slurm_toolkit",
    version="0.4.0a0",
    author="James Byrne",
    author_email="jambyr@bas.ac.uk",
    description="Task toolkit and batcher for SLURM HPCs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    keywords='slurm, hpc, tools, batching',
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
            'slurm_batch=slurm_toolkit.cli:main',
        ],
    },
    python_requires='>=3.6, <4',
    install_requires=[
        "Cython",
        "Fabric",
        "jinja2",
        "jsonschema",
        # Why are they not packaging this any more? 
        #"pyslurm==19.5.0.0",
        "pyyaml",
    ],
    include_package_data=True,
)
