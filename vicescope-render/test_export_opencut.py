import math
import unittest
from export_opencut import narration_duration, plan_images


class BundleContractTests(unittest.TestCase):
    def test_audio_requires_one_stream_and_finite_duration(self):
        for streams, duration in [
            ([], "30"), ([{"codec_type": "video"}], "30"),
            ([{"codec_type": "audio"}, {"codec_type": "audio"}], "30"),
            ([{"codec_type": "audio"}], "nan"),
            ([{"codec_type": "audio"}], "0"),
            ([{"codec_type": "audio"}], "301"),
        ]:
            with self.subTest(streams=streams, duration=duration), self.assertRaises(ValueError):
                narration_duration({"streams": streams, "format": {"duration": duration}})
        self.assertEqual(narration_duration({
            "streams": [{"codec_type": "audio"}], "format": {"duration": "31.533"}
        }), 31.533)

    def test_timeline_covers_complete_audio_without_gaps(self):
        for duration in [0.1, 31.533, 300]:
            for count in [1, 3, 7]:
                plan = plan_images(duration, [f"{i}.jpg" for i in range(count)])
                self.assertEqual(plan[0]["start_seconds"], 0)
                self.assertAlmostEqual(plan[-1]["end_seconds"], duration, places=6)
                for previous, current in zip(plan, plan[1:]):
                    self.assertEqual(previous["end_seconds"], current["start_seconds"])
                self.assertTrue(all(item["end_seconds"] > item["start_seconds"] for item in plan))

    def test_invalid_timeline_is_rejected(self):
        for duration, names in [(0, ["a.jpg"]), (math.nan, ["a.jpg"]), (1, [])]:
            with self.subTest(duration=duration, names=names), self.assertRaises(ValueError):
                plan_images(duration, names)


if __name__ == "__main__":
    unittest.main()
