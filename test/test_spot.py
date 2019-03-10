import unittest
import unittest.mock

from spark_emr.spot import spot_price


class TestSpotPrice(unittest.TestCase):
    @unittest.mock.patch("boto3.client")
    def test_spot(self, boto_mock):
        mock = unittest.mock.Mock()
        boto_mock.return_value = mock

        mock.describe_regions.return_value = {
            "Regions": [{"RegionName": "eu-west-2"},
                        {'RegionName': 'eu-north-1'}]
        }
        mock.describe_spot_price_history.side_effect = [
            {
                'SpotPriceHistory': [{
                    'AvailabilityZone': 'eu-west-2a',
                    'InstanceType': 'm4.large',
                    'SpotPrice': '0.029000'}]
            },
            {
                'SpotPriceHistory': [{
                    'AvailabilityZone': 'eu-north-1b',
                    'InstanceType': 'm4.large',
                    'SpotPrice': '0.029000'}]
            },
        ]
        with self.assertRaises(Exception) as context:
            ret = spot_price("m4.large")
            self.assertTrue("We need a list for inst!" in context.exception)
        ret = spot_price(["m4.large"])
        self.assertEqual(ret, [('m4.large', 'eu-west-2a', '0.029000', '0.116'),
                               ('m4.large', 'eu-north-1b', '0.029000', None)])
