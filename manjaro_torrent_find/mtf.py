#!/usr/bin/env python3
"""Manjaro Torrent Find will scrape osdn.net for Manjaro torrents.

Usage:
    mtf [options]

Options:
    -h this help
    -o output directory (default: current directory)
    -p project (either 'manjaro' or 'manjaro-community') (default: both)
    -r only scrape the OSDN RSS feeds to find the torrent files
    -t length of time to wait before requesting a new page/file from OSDN (default: 1 second)

With `-o` the output directory must already exist, otherwise the
current directory is used.

`-t` defaults to 1, though it could be a fracion i.e. 0.25 and is amount of time
to wait before requesting a new 'thing' from OSDN - this is to ensure that we don't
overload the OSDN servers (leave it at 1 second to be nice).
"""

import os
import sys
import time

from bs4 import BeautifulSoup as BS
from getopt2 import getopt2
import requests
from typing import List
from typing import Tuple

endings = ["torrent", "sha1", "sha256", "sig"]
burl = "https://osdn.net"
outdir = os.getcwd()
slow = 1


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
    time.sleep(slow)
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


def osdnWalk(pageurl, path=None, seen=[]):
    """Scrapes the OSDN page for directories and filenames.

    Recurses down the tree of directories adding to the
    output dictionary.

    Args:
        pageurl: the url to scrape

    Returns:
        dict:
        {
        "edition":
            {
            "version":
                ["file1", "file2", ..., "filen"]
            }
        }
    """
    furls = []
    dirs = {}
    xpath = "" if path is None else f"{path}/"
    # checkpoint to test we aren't recursing over and over
    if path is not None:
        tmp = path.split("/")
        if len(tmp) > 4:
            print(f"long path {path}, recursion has probably failed, sorry.")
            sys.exit(1)
    else:
        print(f"requesting start page: {pageurl}")
    if pageurl not in seen:
        seen.append(pageurl)
        time.sleep(slow)
        # print(f"requesting {pageurl}")
        r = requests.get(pageurl)
        if r.status_code == 200:
            hpage = BS(r.text, "lxml")
            rows = hpage.find_all("tr")
            # print(f"found {len(rows)} rows")
            for row in rows:
                url, xclass = extractUrlByClass(row)
                # print(f"url: {url}, class: {xclass}")
                if url is not None:
                    if xclass == "file":
                        # print(f"adding file {url}")
                        furls.append(url)
                    elif xclass == "dir":
                        bname = os.path.basename(url)
                        if url.startswith("/"):
                            url = f"{burl}{url}"
                        else:
                            url = f"{burl}/{url}"
                        print(f"descending into {url}")
                        ypath = f"{xpath}{bname}"
                        xdirs, xfurls = osdnWalk(url, ypath, seen)
                        dirs[ypath] = {"dirs": xdirs, "files": xfurls}
                        # print(f"found: {dirs[ypath]}")
    else:
        print(f"have already seen {pageurl}: seen: {seen}")
    # print(f"returning ({dirs}, {furls})")
    return (dirs, furls)


def extractUrlFromTableRow(trrow):
    """Extracts the url for the file from the table row, trrow."""
    url = None
    row = BS(str(trrow), "lxml")
    tds = row.find_all("td")
    for td in tds:
        atts = td.attrs
        # print(f"td string: {td.string}, attrs: {atts}")
        if atts is not None and "class" in atts and atts["class"][0] == "name":
            # print(f"finding link in {td}. atts: {atts}")
            link = td.find("a")
            if "(Parent folder)" != link.get_text().strip():
                url = link["href"]
                # print(f"string: '{link.get_text().strip()}', url: {url}")
    return url


def extractUrlByClass(row):
    """Extracts the url if the class is file or dir."""
    url = None
    xclass = None
    atts = row.attrs
    # print(f"row: {row} atts: {atts}")
    if atts is not None and "class" in atts:
        xclass = atts["class"][0]
        if xclass in ["file", "dir"]:
            url = extractUrlFromTableRow(row)
    return (url, xclass)


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


def downloadViaRedirect(fn, url, indent="    "):
    time.sleep(slow)
    r = requests.get(f"{url}/{fn}")
    if r.status_code == 200:
        rdir = getRedirectUrl(r.text)
        if rdir.startswith("/"):
            rurl = f"{burl}{rdir}"
        else:
            rurl = f"{burl}/{rdir}"
        time.sleep(slow)
        r = requests.get(rurl)
        if r.status_code == 200:
            outfn = os.path.abspath("/".join([outdir, fn]))
            with open(outfn, "wb") as ofn:
                for chk in r.iter_content():
                    ofn.write(chk)
            print(f"{indent}{fn} saved to {outdir}/{fn}.")
        else:
            print(f"Failed to download via redirect {fn}: status code: {r.status_code}")
    else:
        print(f"failed to get initial url for {fn} status code: {r.status_code}")


def getFile(fn, indent=""):
    for ending in endings:
        if fn.endswith(ending):
            if fn.startswith("/"):
                url = f"{burl}{os.path.dirname(fn)}"
            else:
                url = f"{burl}/{os.path.dirname(fn)}"
            bfn = os.path.basename(fn)
            # print(f"requesting: {url}/{bfn}")
            downloadViaRedirect(bfn, url, indent=indent)
            break


def downloadFiles(dirs):
    for nn in dirs:
        if "dirs" in dirs[nn]:
            downloadFiles(dirs[nn])
        if "files" in dirs[nn]:
            for fn in dirs[nn]["files"]:
                getFile(fn)
    if "files" in dirs:
        for fn in dirs["files"]:
            getFile(fn)


def printDir(dirs, indent=""):
    for nn in dirs:
        print(f"{indent}{nn}")
        if "dirs" in dirs[nn]:
            printDir(dirs[nn]["dirs"], indent=indent + "  ")
        for fn in dirs[nn]["files"]:
            # print(f"{indent}  {os.path.basename(fn)}")
            print(f"{indent}  {fn}")
            getFile(fn, f"{indent}  ")
    if "files" in dirs:
        for fn in dirs["files"]:
            # print(f"{indent}  {os.path.basename(fn)}")
            print(f"{indent}  {fn}")


@getopt2(sys.argv[1:], "ho:p:rt:")
def goBabe(opts: List[Tuple]):
    global outdir, slow
    dorss = False
    projects = ["manjaro", "manjaro-community", "manjaro-archive"]
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
        elif opt == "-t":
            slow = float(arg)
    if dorss:
        for project in projects:
            print(f"Obtaining RSS feed for {project}")
            getRssProject(project)
    else:
        for project in projects:
            dirs, furls = osdnWalk(f"{burl}/projects/{project}/storage")
            printDir(dirs)
            # downloadFiles(dirs)
            # print(f"found: {dirs}")

    if __name__ == "__main__":
        goBabe()
