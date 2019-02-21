# Spark-EMR

[![Build Status](https://api.travis-ci.org/delijati/spark-emr.svg?branch=master)](https://travis-ci.org/delijati/spark-emr)

Run an python package on AWS EMR

## Install

Develop install:

    $ pip install -e .

Testing:

    $ pip install tox
    $ tox

## Setup

The easiest way to get EMR up and running is to go through the Web-Interface
and create a ssh key, and start a cluster by hand. This will then create the
needed subnet_key and EMR roles.

## Config yaml file

Create a ``config.yaml`` per project or as a default into
`~/.config/spark-emr.yaml`

    bootstrap_uri: s3://foo/bar
    master: 
      instance_type: m4.large
      size_in_gb: 100
    core: 
      instance_type: m4.large
      instance_count: 2
      size_in_gb: 100
    ssh_key: XXXXX
    subnet_id: subnet-XXXXXX
    python_version: python36
    emr_version: emr-5.20.0
    consistent: false
    optimization: false
    region: eu-central-1
    job_flow_role: EMR_EC2_DefaultRole 
    service_role: EMR_DefaultRole

## CLI-Interface

### Start

To run a python code on EMR you need to build a proper python package aka
`setup.py` with `console_scripts` the script needs to end on `.py` or yarn
won't be able to execute it |-(

Bootstrap a cluster, install the pypackage, execute the task in cmdline, poll
cluster until finished, stop cluster:

    $ spark-emr start \
    [--config config.yaml] \
    --name "Spark-ETL" \
    --cmdline "etl.py --input s3://in/in.csv --output s3://out/out.csv" \
    --tags foo 2 bar 4 \
    --poll \
    --yarn-log \
    --package "../"

Running with a released pypackage version (pip):

    $ spark-emr start \
    ... \
    --package pip+etl_pypackage

### Status

Returns the status of a cluster (also terminated ones):

    $ spark-emr status --cluster-id j-XXXXX

### List

List all cluster:

    $ spark-emr list [--config config.yaml] [--namespace spark_emr]

### Stop

Stop a running cluster:

    $ spark-emr stop --cluster-id j-XXXXX

# Appendix

### Running commands on EMR

The created command can also be run directly from the master:

    $ /usr/bin/spark-submit \
    --deploy-mode cluster \
    --master yarn \
    --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=python35 \
    --conf spark.executorEnv.PYSPARK_PYTHON=python35 \
    /usr/local/bin/etl.py --input s3://in/in.csv --output s3://out/out.csv

### Running commands on docker

    $ docker run --rm -ti -v `pwd`/test/dummy:/app/work spark-base \
    bash -c "cd /app/work && pip3 install -e . && spark_emr_dummy.py 10"
