"""Fixture tests for ccattention. Run: python3 test/test.py

Each case is a mistake the tool made; every run uses a temporary HOME, so
real transcripts are never read.
"""
import datetime
import json
import os
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bin", "ccattention")


def run(home, *args, tz="Asia/Tokyo"):
    env = dict(os.environ, HOME=home, TZ=tz, CCATTENTION_LANG="en")
    return subprocess.run([sys.executable, BIN, *args], env=env, capture_output=True, text=True)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = self.tmp.name
        proj = os.path.join(self.home, ".claude", "projects", "-p-a")
        os.makedirs(proj)
        # The most recent 23:00 UTC: 08:00 the next morning in Tokyo.
        now = datetime.datetime.now(datetime.timezone.utc)
        t = now.replace(hour=23, minute=0, second=0, microsecond=0)
        if t > now:
            t -= datetime.timedelta(days=1)
        self.utc_day = t.date().isoformat()
        self.tokyo_day = (t + datetime.timedelta(hours=9)).date().isoformat()
        lines = []
        for i in range(3):
            at = t + datetime.timedelta(minutes=2 * i)
            lines.append({"type": "user", "timestamp": at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                          "message": {"role": "user", "content": f"please do thing {i}"}})
            lines.append({"type": "assistant",
                          "timestamp": (at + datetime.timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                          "message": {"role": "assistant", "content": [{"type": "text", "text": "ok"}]}})
        with open(os.path.join(proj, "s.jsonl"), "w") as f:
            f.write("\n".join(json.dumps(x) for x in lines) + "\n")

    def tearDown(self):
        self.tmp.cleanup()


class LocalDays(Base):
    def test_day_is_the_local_day_not_utc(self):
        r = run(self.home, "--days", "3", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(list(json.loads(r.stdout)), [self.tokyo_day])

    def test_utc_zone_still_reads_utc_day(self):
        r = run(self.home, "--days", "3", "--json", tz="UTC")
        self.assertEqual(list(json.loads(r.stdout)), [self.utc_day])

    def test_week_starts_on_the_local_monday(self):
        d = datetime.date.fromisoformat(self.tokyo_day)
        monday = (d - datetime.timedelta(days=d.weekday())).isoformat()
        r = run(self.home, "--days", "3", "--weekly", "--json")
        self.assertEqual(list(json.loads(r.stdout)), [monday])


if __name__ == "__main__":
    unittest.main(verbosity=2)
