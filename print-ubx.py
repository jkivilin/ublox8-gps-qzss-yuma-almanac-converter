#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pyubx2 import UBXReader

if __name__ == "__main__":
  with open(sys.argv[1], "rb") as inputfile:
    ubr = UBXReader(inputfile, ubxonly = True)
    for (raw_data, parsed_data) in ubr:
      print(parsed_data)
