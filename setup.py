import os

from setuptools import find_packages, setup

version = "0.1.1"

here = os.path.abspath(os.path.dirname(__file__))
CHANGES = open(os.path.join(here, "CHANGES.md")).read()
README = open(os.path.join(here, "README.md")).read()

setup(
    name="spark_emr",
    version=version,
    description="Run python packages on AWS EMR",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="AWS EMR SPARK PYSPARK",
    author="Josip Delic",
    author_email="delijati@gmx.net",
    url="https://www.github.com/delijati/spark-emr",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "boto3",
        "loguru",
        "pyyaml",
        "spark-optimizer",
        # we need this to get tox working
        "pluggy>=0.7",
    ],
    test_suite="test",
    entry_points={
        "console_scripts": [
            "spark-emr = spark_emr.__main__:main"
        ],
    }
)
