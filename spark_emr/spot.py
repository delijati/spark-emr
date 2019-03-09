import boto3
import datetime
import collections.abc
from spark_optimizer.optimizer import load_emr_instance


def spot_price(inst, region="us-west-2"):
    if not isinstance(inst, collections.abc.Sequence) or isinstance(inst, str):
        raise Exception("We need a list for inst!")

    client = boto3.client('ec2', region_name=region)
    regions = [x["RegionName"] for x in client.describe_regions()["Regions"]]

    results = []

    for region in regions:
        client = boto3.client('ec2', region_name=region)
        prices = client.describe_spot_price_history(
            InstanceTypes=inst,
            ProductDescriptions=['Linux/UNIX', 'Linux/UNIX (Amazon VPC)'],
            StartTime=(datetime.datetime.now() +
                       datetime.timedelta(days=1)).isoformat(),
            MaxResults=len(inst)
        )
        for price in prices["SpotPriceHistory"]:
            emr_info = load_emr_instance()[price["InstanceType"]]
            ondemand = (emr_info.get("pricing", {})
                        .get(region,  {})
                        .get("ec2"))
            results.append(
                (price["InstanceType"],
                 price["AvailabilityZone"],
                 price["SpotPrice"],
                 ondemand
                 )
            )

    ret = sorted(results, key=lambda x: x[2])
    return ret
