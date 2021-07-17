#!/usr/bin/python3.4
#-*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from views.CmdView.command_line import CommandLine

def main(args=None):
    CommandLine().process()


if __name__ == "__main__":
    main() 
