#!/usr/bin/env python
import sys

from epic.epic_runner import EpicRunner


class twmn_core(EpicRunner):
    pass


if __name__ == "__main__":
    twmn = twmn_core(plugin_dirs=["libexec"])
    twmn.run(sys.argv[1:])
