import spark_emr.util

from spark_emr.const import SH_YARN_LOG

YARN_LOG = """
#!/bin/bash
set -x

LOCAL_DIR=/home/hadoop/yarn_logs
mkdir $LOCAL_DIR

for row in $( yarn application -appStates ALL -list | awk '/application_/{print $1 "," $2}' )
do
    fields=($(echo $row | tr "," "\n"))
    yarn logs -applicationId ${fields[0]} > $LOCAL_DIR/yarn_${fields[0]}_${fields[1]}.log
done
if [ -z "$(ls -A $LOCAL_DIR)" ]; then
    echo "($LOCAL_DIR) is empty"
else
    aws s3 cp $LOCAL_DIR/*.log %s
fi
"""  # noqa


def spark_yarn_log_step(bootstrap_base, region):
    s3mgr = spark_emr.util.S3Manager(region)
    uri = bootstrap_base.file_append(SH_YARN_LOG)
    yarn_log_sh = YARN_LOG % bootstrap_base.folder_uri
    s3mgr.put_content(target_uri=uri, content=yarn_log_sh)

    script = "/home/hadoop/%s" % SH_YARN_LOG
    cmd = "aws s3 cp {src} {script} && chmod +x {script} && bash {script}"
    cmd = cmd.format(src=uri.uri, script=script)

    step = {
        "Name": "Yarn log to s3",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": ["bash", "-c", "%s" % cmd],
        },
        "ActionOnFailure": "CONTINUE",
    }
    return step


def spark_step(name,
               command,
               python_version,
               action_on_failure):

    ACTION_ON_FAILURE = ["TERMINATE_JOB_FLOW", "TERMINATE_CLUSTER",
                         "CANCEL_AND_WAIT", "CONTINUE"]
    if action_on_failure not in ACTION_ON_FAILURE:
        raise Exception("Wrong <<ActionOnFailure:%s>> use <<working:%s>>" % (
            action_on_failure, "|".join(ACTION_ON_FAILURE)))

    configuration = {
        "Name": name,
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit", "--deploy-mode", "cluster", "--master",
                "yarn",
                "--conf",
                "spark.yarn.appMasterEnv.PYSPARK_PYTHON=%s" % python_version,
                "--conf",
                "spark.executorEnv.PYSPARK_PYTHON=%s" % python_version,
            ],
        },
        "ActionOnFailure": action_on_failure,
    }

    args = [x.strip() for x in command.split()]
    args[0] = "/usr/local/bin/%s" % args[0]
    configuration["HadoopJarStep"]["Args"].extend(args)
    return configuration
