#!/usr/bin/env python3
"""Manjaro Torrent Find will scrape osdn.net for Manjaro torrents."""

import sys

import requests
from bs4 import BeautifulSoup as BS

projects = ["manjaro", "manjaro-community"]
endings = ["torrent", "sha1", "sha256", "sig"]
burl = "https://osdn.net"


def getRSSFeed(rssurl):
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


def getProject(project):
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
            with open(fn, "wb") as ofn:
                for chk in r.iter_content():
                    ofn.write(chk)
            print(f"    {fn} saved ok.")
        else:
            print(f"Failed to download via redirect {fn}: status code: {r.status_code}")
    else:
        print(f"failed to get initial url for {fn} status code: {r.status_code}")


def goBabe():
    for project in projects:
        print(project)
        getProject(project)


if __name__ == "__main__":
    goBabe()
