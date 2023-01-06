'''Bulk download audio files from tokybook.com'''

from pathlib import Path
from typing import MutableMapping
from urllib.request import urlopen, Request
import argparse
import html
import logging
import time


WELCOME_FILE = 'welcome-you-to-tokybook.mp3'
HEADERS: MutableMapping[str, str] = {'User-Agent':  "Magic Browser"}
URL_BASE = 'https://files02.tokybook.com/audio/'  # file source directory
URL_FLAG = 'chapter_link_dropbox'
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    '''argument parsing'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', required=True)
    parser.add_argument('--debug', '-d', action='store_true', default=False)
    parser.add_argument('--dry-run', action='store_true', default=False)
    args = parser.parse_args()
    return args


def download_file(dir_title: str, file_name: str, url: str,
                  dry_run: bool) -> None:
    '''helper function to download a file to a specific subdir'''
    download_path = Path(dir_title, file_name)
    log.debug("Downloading %s to %s", url, download_path)
    if not dry_run:
        page_request = Request(url, headers=HEADERS)
        with (urlopen(page_request) as page_connection,
              open(download_path, 'wb') as audio_file):
            audio_file.write(page_connection.read())
    time.sleep(3)


def main():
    '''main script to download audio books'''
    args = parse_args()
    if args.debug:
        log.setLevel(logging.DEBUG)

    page_request = Request(args.url, headers=HEADERS)
    with urlopen(page_request) as page_connection:
        page = page_connection.read().decode('utf-8')

    for line in page.split('\n'):
        if '<title>' in line:
            # create file directory from book title
            dir_title = html.unescape(line[17:-40])
            if " " in dir_title:
                dir_title = dir_title.replace(" ", "_")
            log.debug("Creating directory %s to download files to", dir_title)
            Path(dir_title).mkdir(exist_ok=True)
        if WELCOME_FILE in line:
            log.debug('Skipping %s', WELCOME_FILE)
        else:
            if URL_FLAG in line:
                url_suffix = line[45:-2]
                if ' ' in url_suffix:  # encode spaces for url
                    url_suffix = url_suffix.replace(" ", "%20")
                    url = (URL_BASE + url_suffix)
                    if '\\' in url:
                        # removing \ that might cause errors in file names.
                        # \ doesn't always error
                        url = url.replace('\\', "")  # final mp3 file name

                        file_name = url_suffix.split('/')[-1]\
                            .replace('%20', '_')
                        download_file(dir_title, file_name, url, args.dry_run)

                    else:
                        print('error')
                else:
                    # catch for when there are no spaces in var new
                    # only one case found. same work as above
                    if '\\' in url_suffix:
                        url_suffix = url_suffix.replace('\\', "")
                        url = (URL_BASE + url_suffix)

                        file_name = url_suffix.split('/')[-1]\
                            .replace('%20', '_')
                        download_file(dir_title, file_name, url, args.dry_run)


if __name__ == "__main__":
    main()
