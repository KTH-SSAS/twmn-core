#!/usr/bin/env python3
import sys

from epic.epic_completions import EpicCompletion

class TwmnCompletion(EpicCompletion):
    '''
    Any twmn specific stuff can be implemented here.
    '''
    pass

if __name__ == "__main__":
    twmn = TwmnCompletion(command_dirs=["libexec"])
    twmn.complete(sys.argv)