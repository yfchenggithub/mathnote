"""Reject stale, missing, and ambiguous C002 share associations."""

import copy
import json
import unittest

from verify_share_assets import REGISTRY, UID_ROOT, validate


class ShareAssetTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def validate_changed(self, data):
        return validate(UID_ROOT, data=data)

    def test_real_pair(self):
        self.assertEqual(validate()["associations"], 1)

    def test_duplicate_display_asset_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["associations"].append(copy.deepcopy(data["associations"][0]))
        with self.assertRaisesRegex(ValueError, "one-to-one"):
            self.validate_changed(data)

    def test_wrong_video_hash_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["associations"][0]["shareSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "mismatched shareSource"):
            self.validate_changed(data)

    def test_missing_video_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["associations"][0]["shareSource"] = "videos/missing.mp4"
        with self.assertRaisesRegex(ValueError, "missing or mismatched shareSource"):
            self.validate_changed(data)


if __name__ == "__main__":
    unittest.main()
