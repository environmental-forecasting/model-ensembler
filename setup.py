import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slurm_toolkit",
    version="0.1.0",
    author="James Byrne",
    author_email="jambyr@bas.ac.uk",
    description="Job toolkit and batcher for SLURM HPCs facilitating external constraint management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
    ],
    entry_points={
        'console_scripts': [
            'slurm_batch=slurm_toolkit.cli:main',
        ],
    },
)
