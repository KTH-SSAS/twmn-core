#!/usr/bin/env python
import sys

from epic.epic_runner import EpicRunner


class TwmnCore(EpicRunner):
    '''
    Any twmn specific stuff can be implemented here.
    '''
    pass


if __name__ == "__main__":
    twmn = TwmnCore(command_dirs=["libexec"])
    twmn.run(sys.argv[1:])
