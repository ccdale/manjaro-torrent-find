Manjaro Torrent Find
====================

Reads the RSS feed from osdn.net/projects/manjaro/storage/!rss and parses out the
.torrent, .sig, .sha1 and .sha256 files. It then attempts to download them to the
current directory.

Installation
------------

Available from pypi, so `pip3 install manjaro-torrent-find --user` should suffice.
You'll then have a new command at `$HOME/.local/bin/mtf` so add that dir to your path.

Usage
-----

Once the local python scripts directory is on your path, just execute `mtf`.

```
Manjaro Torrent Find will scrape osdn.net for Manjaro torrents.

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

```
