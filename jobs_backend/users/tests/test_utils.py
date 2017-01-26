import unittest

from .. import utils


class UIDTest(unittest.TestCase):

    def test_ok_encode_uid(self):
        self.assertEqual(utils.encode_uid(1), 'MQ')
        self.assertEqual(utils.encode_uid(999), 'OTk5')
        self.assertEqual(
            utils.encode_uid('user@example.com'), 'dXNlckBleGFtcGxlLmNvbQ'
        )

    def test_ok_decode_uid(self):
        self.assertEqual(utils.decode_uid('MQ'), '1')
        self.assertEqual(utils.decode_uid('OTk5'), '999')
        self.assertEqual(
            utils.decode_uid('dXNlckBleGFtcGxlLmNvbQ'), 'user@example.com'
        )
