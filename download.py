import argparse
import re
import time
import subprocess
import sys
import glob
import os
import requests

from bs4 import BeautifulSoup


def joinanddelete(lfile, namev):
    try:
        cp = subprocess.run(
            [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                "{}.txt".format(lfile),
                "-c",
                "copy",
                namev,
            ],
            capture_output=True,
            check=True,
            text=True,
        )

        print(cp.stdout)
    except subprocess.CalledProcessError as cpe:
        print(cpe.stderr, end="")
        sys.exit(cpe.returncode)

    del_files = glob.glob("{}.*".format(lfile))

    for file_name in del_files:
        try:
            os.remove(file_name)
        except OSError as e:
            print(f"Error deleting {file_name}: {e}")


def current_milli_time():
    return round(time.time() * 1000)


def download_file(url, local_filename):
    with requests.get(url, stream=True, timeout=10) as r:
        try:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.HTTPError as e:
            return False
        except requests.exceptions.RequestException as e:
            print("A request error occurred:", e)
            return False
    return True


parser = argparse.ArgumentParser("params")
parser.add_argument(
    "url", help="The URL where the program is stored on archive.org", type=str
)
args = parser.parse_args()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

page = requests.get(args.url, headers=headers, timeout=10)

soup = BeautifulSoup(page.content, "html.parser")

item = soup.find("img", attrs={"data-idx": True})

namevideourl = soup.find("meta", attrs={"property": "og:video"})

namevideo = ((namevideourl["content"]).split("/"))[-1]
fileextension = namevideo.split(".")[-1]

result = re.findall("^(.+).thumbs", item["src"])
urltodowload = f"https:{result[0]}.{fileextension}"
INCREMENT = 60
start = 0
end = start + INCREMENT
localfile = current_milli_time()
fileversion = 0
filelist = open(f"{localfile}.txt", "a")
while True:
    downurl = f"{urltodowload}?start={start}&end={end}"

    print(f"Downloading part {fileversion}")

    ok = download_file(
        downurl, f"{localfile}.{fileversion}.{fileextension}"
    )

    if not ok:
        break

    filelist.write(f"file '{localfile}.{fileversion}.{fileextension}'\n")

    start += INCREMENT
    end += INCREMENT
    fileversion += 1
    time.sleep(3)

filelist.close()
joinanddelete(localfile, namevideo)
print("Finished.")
