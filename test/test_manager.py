import unittest
import os
import moto
import spark_emr.util
import spark_emr.manager

HERE = os.path.dirname(os.path.abspath(__file__))
DUMMY_FOLDER = os.path.join(HERE, "dummy")
CONFIG = os.path.join(HERE, "config.yaml")


class TestEMRManager(unittest.TestCase):

    def _create_bucket(self, bucket):
        import boto3
        client = boto3.client('s3', region_name='eu-central-1')
        client.create_bucket(Bucket=bucket)
        return client

    def xxtest_start(self):
        # need a fix https://github.com/spulec/moto/issues/1708
        with moto.mock_s3():
            with moto.mock_emr():
                config = spark_emr.util.load_config(CONFIG)
                bootstrap_path = spark_emr.util.S3Path(config["bootstrap_uri"])
                self._create_bucket(bootstrap_path.bucket)
                emr = spark_emr.manager.EmrManager(config)
                job_flow_id = emr.start(
                    "TEST-EMR",
                    "spark_emr_dummy.py 10",
                    DUMMY_FOLDER,
                    {},
                    False,
                    False)
                self.assertIsNotNone(job_flow_id)

    def test_list(self):
        with moto.mock_s3():
            with moto.mock_emr():
                config = spark_emr.util.load_config(CONFIG)
                ret = spark_emr.manager.list("spark_emr", config["region"])
                self.assertEqual(ret, [])
