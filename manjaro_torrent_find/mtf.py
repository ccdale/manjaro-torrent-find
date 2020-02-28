#!/usr/bin/env python3
"""Manjaro Torrent Find will scrape osdn.net for Manjaro torrents.

Usage:
    mtf [options]

Options:
    -h this help
    -o output directory (default: current directory)
    -p project (either 'manjaro' or 'manjaro-community') (default: both)
    -r only scrape the OSDN RSS feeds to find the torrent files

With `-o` the output directory must already exist, otherwise the
current directory is used.
"""

import os
import sys

from bs4 import BeautifulSoup as BS
from getopt2 import getopt2
import requests
from typing import List
from typing import Tuple

projects = ["manjaro", "manjaro-community"]
endings = ["torrent", "sha1", "sha256", "sig"]
burl = "https://osdn.net"
outdir = os.getcwd()


def usage():
    sys.exit(f"{__doc__}")


def getRSSFeed(rssurl):
    """Scrapes the RSS feed for filenames.

    Args:
        rssurl: the rssurl to download

    Returns:
        dict:
        {
        "edition":
             {"version":
                 ["file1", "file2", ..., "filen"]
             }
        }
    """
    fns = None
    r = requests.get(rssurl)
    if r.status_code == 200:
        rss = BS(r.text, "lxml")
        items = rss.find_all("item")
        fns = {}
        for item in items:
            tmp = item.title.string.split("/")
            if tmp[1] not in fns:
                fns[tmp[1]] = {}
            if tmp[2] not in fns[tmp[1]]:
                fns[tmp[1]][tmp[2]] = []
            fns[tmp[1]][tmp[2]].append(tmp[3])
    return fns


def getRedirectUrl(xstr):
    bhtml = BS(xstr, "html.parser")
    ps = bhtml.find_all("p")
    for p in ps:
        if p.a is not None:
            if "href" in p.a.attrs:
                return p.a.attrs["href"]


def getVersion(version, url):
    for fn in version:
        for ending in endings:
            if fn.endswith(ending):
                # print(f"    {fn}")
                downloadViaRedirect(fn, url)


def getEdition(edition, url):
    for version in edition:
        print(f"  {version}")
        getVersion(edition[version], f"{url}/{version}")


def getRssProject(project):
    purl = f"{burl}/projects/{project}/storage"
    rssurl = f"{purl}/!rss"
    fns = getRSSFeed(rssurl)
    # print(fns)
    for edition in fns:
        print(f"{edition}")
        getEdition(fns[edition], f"{purl}/{edition}")


def downloadViaRedirect(fn, url):
    r = requests.get(f"{url}/{fn}")
    if r.status_code == 200:
        rdir = getRedirectUrl(r.text)
        if rdir.startswith("/"):
            rurl = f"{burl}{rdir}"
        else:
            rurl = f"{burl}/{rdir}"
        r = requests.get(rurl)
        if r.status_code == 200:
            outfn = os.path.abspath("/".join([outdir, fn]))
            with open(outfn, "wb") as ofn:
                for chk in r.iter_content():
                    ofn.write(chk)
            print(f"    {fn} saved ok to {outdir}.")
        else:
            print(f"Failed to download via redirect {fn}: status code: {r.status_code}")
    else:
        print(f"failed to get initial url for {fn} status code: {r.status_code}")


@getopt2(sys.argv[1:], "ho:p:r")
def goBabe(opts: List[Tuple]):
    dorss = False
    for opt, arg in opts:
        if opt == "-h":
            usage()
        elif opt == "-o":
            if os.path.isdir(arg):
                outdir = arg
        elif opt == "-p":
            projects = [arg]
        elif opt == "-r":
            dorss = True
    if dorss:
        for project in projects:
            print(f"Obtaining RSS feed for {project}")
            getRssProject(project)

    if __name__ == "__main__":
        goBabe()
