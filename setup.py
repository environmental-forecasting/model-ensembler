import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hpc_batcher",
    version="0.0.1",
    author="James Byrne",
    author_email="jambyr@bas.ac.uk",
    description="Job batcher for HPCs facilitating external constraint management",
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
            'hpc_batch=hpc_batcher:main',
        ],
    },
)
