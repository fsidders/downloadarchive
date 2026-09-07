import argparse
import requests
import re
import time
import subprocess
import sys
import glob
import os
from bs4 import BeautifulSoup


def joinanddelete(localfile, namevideo):
    try:
        cp = subprocess.run(
            [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                "{}.txt".format(localfile),
                "-c",
                "copy",
                namevideo,
            ],
            capture_output=True,
            check=True,
            text=True,
        )

        print(cp.stdout)
    except subprocess.CalledProcessError as cpe:
        print(cpe.stderr, end="")
        sys.exit(cpe.returncode)

    log_files = glob.glob("{}.*".format(localfile))
    print(f"Found files: {log_files}")

    for file_name in log_files:
        try:
            os.remove(file_name)
            print(f"Deleted: {file_name}")
        except OSError as e:
            print(f"Error deleting {file_name}: {e}")


def current_milli_time():
    return round(time.time() * 1000)


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        try:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.HTTPError as e:
            print("HTTP error occurred:", e)
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

page = requests.get(args.url, headers=headers)

soup = BeautifulSoup(page.content, "html.parser")

item = soup.find("img", attrs={"data-idx": True})

namevideourl = soup.find("meta", attrs={"property": "og:video"})

namevideo = ((namevideourl["content"]).split("/"))[-1]

result = re.findall("^(.+).thumbs", item["src"])
urltodowload = "https:{}.mp4".format(result[0])
increment = 60
start = 0
end = start + increment
localfile = current_milli_time()
fileextension = 0
filelist = open("{}.txt".format(localfile), "a")
while True:
    downurl = "{}?start={}&end={}".format(urltodowload, start, end)
    ok = download_file(downurl, "{}.{}.mp4".format(localfile, fileextension))

    if not ok:
        break

    filelist.write("file '{}.{}.mp4'\n".format(localfile, fileextension))

    start += increment
    end += increment
    fileextension += 1
    time.sleep(3)

filelist.close()
joinanddelete(localfile, namevideo)
