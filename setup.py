# setup.py

from setuptools import setup, find_packages

setup(
    name="funcversion",
    version="0.1.3",
    description="A Python library for managing multiple versions of functions using decorators.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pizzaface",
    url="https://github.com/pizzaface/funcversion",  # Replace with your repository URL
    packages=find_packages(),
    include_package_data=True,  # Ensure package data is included
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={
        "funcversion": ["py.typed"],
    },
    python_requires=">=3.11",
)
