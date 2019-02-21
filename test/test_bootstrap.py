import unittest
import os
import moto

import spark_emr.bootstrap
from spark_emr.const import PYTHON_VERSION


class TestBootstrap(unittest.TestCase):

    REGION = "eu-central-1"
    PYTHON_VERSION = "python35"
    BUCKET = "foocket"

    def _create_bucket(self):
        import boto3
        client = boto3.client('s3', region_name='eu-central-1')
        client.create_bucket(Bucket=self.BUCKET)
        return client

    def test_python_action(self):
        with moto.mock_s3():
            client = self._create_bucket()
            path = spark_emr.util.S3Path("s3://%s/barky" % self.BUCKET)
            bm = spark_emr.bootstrap.BootstrapManager(
                self.REGION, self.PYTHON_VERSION, path)
            step = bm._python_action()

            expected = {
                "Path": "s3://%s/barky/install_python.sh" % self.BUCKET,
                "Args": []

            }
            self.assertEqual(step["ScriptBootstrapAction"], expected)
            self.assertEqual(
                "barky/install_python.sh",
                client.list_objects(Bucket=self.BUCKET)['Contents'][0]["Key"]
            )
            obj = client.get_object(
                Bucket=self.BUCKET,
                Key="barky/install_python.sh")

            script = spark_emr.bootstrap.INSTALL_PYTHON.format(
                pv=self.PYTHON_VERSION,
                pvs=PYTHON_VERSION[self.PYTHON_VERSION])
            self.assertEqual(obj["Body"].read().decode("utf-8"), script)

    def test_pypi_action(self):
        with moto.mock_s3():
            client = self._create_bucket()
            path = spark_emr.util.S3Path("s3://%s/barky" % self.BUCKET)
            bm = spark_emr.bootstrap.BootstrapManager(
                self.REGION, self.PYTHON_VERSION, path)

            mypkg = "pip+mypkg==1.0.2"

            step = bm._pypi_action(mypkg)

            expected = {
                "Path": "s3://%s/barky/install_pypi_pypackage.sh" %
                self.BUCKET, "Args": []}
            self.assertEqual(step["ScriptBootstrapAction"], expected)
            self.assertEqual(
                "barky/install_pypi_pypackage.sh",
                client.list_objects(Bucket=self.BUCKET)['Contents'][0]["Key"]
            )

            obj = client.get_object(Bucket=self.BUCKET,
                                    Key="barky/install_pypi_pypackage.sh")

            script = spark_emr.bootstrap.INSTALL_PYPI.format(
                index_url="https://pypi.org/simple",
                package=mypkg.split("+")[1])
            self.assertEqual(obj["Body"].read().decode("utf-8"), script)

    def test_create_pypackage(self):
        bm = spark_emr.bootstrap.BootstrapManager(
            self.REGION, self.PYTHON_VERSION, "")
        package = os.path.dirname(os.path.dirname(__file__))

        temp_file = bm._create_pypackage(package)

        self.assertTrue(temp_file.endswith('.whl'))

    def test_local_pypackage_action(self):
        with moto.mock_s3():
            client = self._create_bucket()
            path = spark_emr.util.S3Path("s3://%s/barky" % self.BUCKET)
            bm = spark_emr.bootstrap.BootstrapManager(
                self.REGION, self.PYTHON_VERSION, path)
            package = os.path.dirname(os.path.dirname(__file__))
            step = bm._local_pypackage_action(package)

            expected = {
                "Path": "s3://%s/barky/install_local_pypackage.sh" %
                self.BUCKET,
                "Args": []}
            self.assertEqual(step["ScriptBootstrapAction"],
                             expected)
            self.assertEqual(
                "barky/install_local_pypackage.sh",
                client.list_objects(Bucket=self.BUCKET)['Contents'][0]["Key"]
            )

            obj = client.get_object(Bucket=self.BUCKET,
                                    Key="barky/install_local_pypackage.sh")

            self.assertTrue("aws s3 cp" in obj["Body"].read().decode("utf-8"))
