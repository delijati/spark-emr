import unittest

import moto

from spark_emr.step import spark_yarn_log_step, spark_step
from spark_emr.util import S3Path


class TestSparkStep(unittest.TestCase):
    def test_spark_step(self):
        name = 'etl'
        command = "etl.py --in in.parquet --out out.parquet"

        configuration = spark_step(name, command, "python35", "CONTINUE")

        self.assertTrue(isinstance(configuration, dict))
        self.assertEqual(name, configuration['Name'])
        self.assertEqual(configuration.get('ActionOnFailure'), 'CONTINUE')
        self.assertEqual(len(configuration['HadoopJarStep']['Args']), 14)
        self.assertTrue("/usr/local/bin/etl.py" in configuration[
            'HadoopJarStep']['Args'])

    def test_yarn_log_step(self):
        with moto.mock_s3():
            # needed for moto
            import boto3
            client = boto3.client('s3', region_name='eu-central-1')
            client.create_bucket(Bucket='bucket')

            base_uri = S3Path("s3://bucket/folder")
            step = spark_yarn_log_step(base_uri, "eu-central-1")

            self.assertTrue(isinstance(step, dict))
            self.assertEqual(step["HadoopJarStep"]["Args"], [
                'bash', '-c',
                'aws s3 cp s3://bucket/folder/yarn_log.sh /home/hadoop/yarn_log.sh && chmod +x /home/hadoop/yarn_log.sh && bash /home/hadoop/yarn_log.sh'
            ])  # noqa
