import io
import os
import json
import zipfile
import argparse
import urllib.request
import multiprocessing
from os.path import join as pjoin

import tqdm
import numpy as np

import textworld
from textworld.logic import State, Rule
from textworld.generator.inform7 import Inform7Game


ZIP_FILENAME = "TextWorld_CoG2019_train.zip"
GAMES_URL = "https://competitions.codalab.org/my/datasets/download/4353feda-a5f7-406a-b49e-aab0b94dd3a8"
MIN_DATAPOINTS_PER_GAME = 100


def download(url, filename=None, force=False):
    filename = filename or url.split('/')[-1]

    if os.path.isfile(filename) and not force:
        return filename

    def _report_download_status(chunk_id, max_chunk_size, total_size):
        size = chunk_id * max_chunk_size / 1024**2
        size_total = total_size / 1024**2
        unit = "Mb"
        if size <= size_total:
            print("{:.1f}{unit} / {:.1f}{unit}".format(size, size_total, unit=unit), end="\r")

    filename, _ = urllib.request.urlretrieve(url, filename, _report_download_status)
    return filename


def extract_games(zip_filename, dst):
    zipped_file = zipfile.ZipFile(zip_filename)
    filenames_to_extract = [f for f in zipped_file.namelist() if f.endswith(".ulx") or f.endswith(".json")]

    if not os.path.isdir(dst):
        os.makedirs(dst)

    print("Extracting...")
    extracted_files = []
    for filename in tqdm.tqdm(filenames_to_extract):
        out_file = pjoin(dst, os.path.basename(filename))
        extracted_files.append(out_file)
        if os.path.isfile(out_file):
            continue

        data = zipped_file.read(filename)
        with open(out_file, "wb") as f:
            f.write(data)

    return extracted_files


def build_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--games_dir", default="./TextWorld_CoG2019_games/",
                        help="Folder where to extract the downloaded games.")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Overwrite existing files.")
    return parser


def main():
    parser = build_argparser()
    args = parser.parse_args()

    filename = download(GAMES_URL, filename=ZIP_FILENAME, force=args.force)
    extract_games(filename, dst=args.games_dir)


if __name__ == "__main__":
    main()
