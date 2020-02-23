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
