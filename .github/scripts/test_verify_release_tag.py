import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class ReleaseTagTest(unittest.TestCase):
    def test_tag_lookup_and_api_failures(self):
        script = Path(__file__).with_name("verify-release-tag.sh")
        with tempfile.TemporaryDirectory() as directory:
            gh = Path(directory) / "gh"
            gh.write_text("""#!/usr/bin/env bash
if [[ "$2" == */git/ref/tags/* ]]; then
  case "$CASE" in
    missing) echo 'gh: Not Found (HTTP 404)' >&2; exit 1 ;;
    forbidden) echo 'gh: Forbidden (HTTP 403)' >&2; exit 1 ;;
    network) echo 'network unavailable' >&2; exit 1 ;;
  esac
else
  case "$CASE" in
    missing) echo 'gh: No commit found for SHA (HTTP 422)' >&2; exit 1 ;;
    different) echo wrong-commit ;;
    resolve-failed) echo 'gh: Service Unavailable (HTTP 503)' >&2; exit 1 ;;
    *) echo expected-commit ;;
  esac
fi
""")
            gh.chmod(0o700)
            for case, expected in [
                ("same", 0),
                ("missing", 0),
                ("different", 1),
                ("forbidden", 1),
                ("network", 1),
                ("resolve-failed", 1),
            ]:
                with self.subTest(case=case):
                    env = {
                        **os.environ,
                        "PATH": directory + os.pathsep + os.environ["PATH"],
                        "GITHUB_REPOSITORY": "testingraphael/koan-raph",
                        "CASE": case,
                    }
                    result = subprocess.run(
                        ["bash", str(script), "v0.67.8", "expected-commit"],
                        env=env,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
