import os
import loguru

from urllib.parse import urlparse

import yaml

import boto3

log = loguru.logger


class S3Path(object):
    def __init__(self, uri):
        if isinstance(uri, S3Path):
            uri = uri.uri
        self.uri = uri
        self.parsed = urlparse(uri)

    @property
    def folder_uri(self):
        if self.uri.endswith("/"):
            return self.uri
        return self.uri + "/"

    @property
    def path(self):
        return os.path.split(self.key)[0]

    @property
    def bucket(self):
        return self.parsed.netloc

    @property
    def key(self):
        return self.parsed.path.lstrip("/")

    @property
    def file(self):
        return os.path.basename(self.parsed.path)

    def file_append(self, name):
        new_url = os.path.join(self.parsed.geturl(), name)
        return S3Path(new_url)

    def __eq__(self, other):
        return self.uri == other.uri

    def __repr__(self):
        return "<<%s:%s>>" % (self.__class__.__name__, self.uri)


class S3Manager(object):

    def __init__(self, region):
        self.region = region
        self.s3c = boto3.client('s3', region_name=region)
        self.s3res = boto3.resource('s3', region_name=region)

    def delete(self, key, bucket):
        if self.s3res.Bucket(bucket) in self.s3res.buckets.all():
            self.s3c.delete_object(Bucket=bucket, Key=key)

    def delete_all(self, bucket):
        bucket = self.s3res.Bucket(bucket)
        bucket.objects.all().delete()

    def put_content(self, target_uri, content):
        self.s3c.put_object(
            Body=content, Bucket=target_uri.bucket, Key=target_uri.key)
        return target_uri

    def upload(self, local, target_uri):
        if self.s3res.Bucket(
                target_uri.bucket) not in self.s3res.buckets.all():
            self.s3res.create_bucket(
                Bucket=target_uri.bucket,
                CreateBucketConfiguration={'LocationConstraint': self.region})
        self.s3c.upload_file(local, target_uri.bucket, target_uri.key)
        return target_uri.uri


def load_config(path):
    if not os.path.exists(path):
        raise Exception("Config file not found!")
    config = yaml.load(open(path, 'r'))
    return config
