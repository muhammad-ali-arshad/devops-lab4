"""Install a matching Chrome for Testing and ChromeDriver pair during image build."""

import json
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path


MANIFEST = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
ROOT = Path("/opt/chrome")


def main():
    with urllib.request.urlopen(MANIFEST, timeout=30) as response:
        stable = json.load(response)["channels"]["Stable"]
    print(f"Installing Chrome and ChromeDriver {stable['version']}", flush=True)
    for name in ("chrome", "chromedriver"):
        url = next(item["url"] for item in stable["downloads"][name] if item["platform"] == "linux64")
        archive = Path("/tmp") / f"{name}.zip"
        urllib.request.urlretrieve(url, archive)
        with zipfile.ZipFile(archive) as package:
            package.extractall(ROOT)
        archive.unlink()
    chrome = ROOT / "chrome-linux64" / "chrome"
    chromedriver = ROOT / "chromedriver-linux64" / "chromedriver"
    chrome.chmod(chrome.stat().st_mode | 0o111)
    chromedriver.chmod(chromedriver.stat().st_mode | 0o111)
    shutil.copy2(chromedriver, "/usr/local/bin/chromedriver")
    os.chmod("/usr/local/bin/chromedriver", 0o755)


if __name__ == "__main__":
    main()
