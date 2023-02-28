** Converter of official QZSS (GPS) Almanac files to u-blox 8 / M8 protocol UBX-MGA almanac messages **

This tool converts YUMA format QZSS+GPS Almanac files to UBX-MGA almanac messages for
u-blox 8 receivers. GPS YUMA almanac data is converted to UBX-MGA-GPS-ALM messages and
QZSS YUMA almanac data to UBX-MGA-QZSS-ALM messages.

Almanac files can be downloaded at:
 - https://sys.qzss.go.jp/dod/en/archives/pnt.html

** Usage **

Usage:
  python3 convert-alm.py [input almanac file] [output UBX file]

Example:
  python3 convert-alm.py qg2021226.alm qg2021226.ubx

** Documentation **

 - https://www.gps.gov/technical/icwg/IS-GPS-200M.pdf
 - https://qzss.go.jp/en/technical/download/pdf/ps-is-qzss/is-qzss-pnt-004.pdf
 - https://content.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf
