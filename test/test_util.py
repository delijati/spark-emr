import unittest

import spark_emr
import spark_emr.util


class TestS3Path(unittest.TestCase):

    def test_main(self):
        parse = spark_emr.util.S3Path(
            "s3://bucket/folder/file.txt")
        self.assertEqual(parse.key, "folder/file.txt")
        self.assertEqual(parse.file, "file.txt")
        self.assertEqual(parse.bucket, "bucket")
        self.assertEqual(parse.path, "folder")
        self.assertEqual(parse.uri, "s3://bucket/folder/file.txt")

    def test_file_append(self):
        parse = spark_emr.util.S3Path("s3://bucket/folder/")
        self.assertEqual(
            parse.file_append("some_file.sh").uri,
            "s3://bucket/folder/some_file.sh")
        parse = spark_emr.util.S3Path("s3://bucket/folder")
        self.assertEqual(
            parse.file_append("some_file.sh").uri,
            "s3://bucket/folder/some_file.sh")

    def test_compare(self):
        first = spark_emr.util.S3Path("s3://bucket/folder/")
        second = spark_emr.util.S3Path("s3://bucket/folder/")
        assert first == second
        # neq
        first = spark_emr.util.S3Path("s3://bucket/folder/")
        second = spark_emr.util.S3Path("s3://bucket/some-folder/")
        assert first != second
