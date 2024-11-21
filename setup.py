# setup.py

from setuptools import setup, find_packages

setup(
    name='funcversion',
    version='0.1.0',
    description='A Python library for managing multiple versions of functions using decorators.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/funcversion',  # Replace with your repository URL
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
