# Reference :  Setup script documentation 
# https://setuptools.readthedocs.io/en/latest/setuptools.html

#!/usr/bin/ev python3
from pathlib import Path
import setuptools

project_dir = Path(__file__).parent


def get_requirements(filename):
    with open(filename) as f:
        requirements = f.read().splitlines()
    return requirements


def get_long_description(filename):
    with open(filename, "r") as fh:
        long_description = fh.read()
    return long_description


setuptools.setup(
    name="checklist-webapp-django",
    version="v1.0",
    author="Chintan Gandhi",
    author_email="cagandhi97@gmail.com",
    description="Checklist webapp in Django",
    long_description=get_long_description("README.md"),
    long_description_content_type="text/markdown",
    keywords=["python"],
    url="https://github.com/cagandhi/Checklist-webapp-Django",
    packages=setuptools.find_packages(),
    install_requires=get_requirements("requirements.txt"),
    include_package_data=True,
    python_requires=">=3.7",
)
