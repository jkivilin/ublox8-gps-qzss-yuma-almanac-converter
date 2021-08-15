#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import struct
from pyubx2 import UBXReader, SET

def ubx_checksum(packet):
  ck_a = 0
  ck_b = 0
  for byte in packet:
    ck_a = (ck_a + byte) & 0xff
    ck_b = (ck_b + ck_a) & 0xff
  return bytes((ck_a, ck_b))

if __name__ == "__main__":
  if ubx_checksum(b"\x06\x01\x02\x00\xf0\x05") != b"\xfe\x16":
    sys.exit(1)

  almanac = {}
  sat_id = 0
  with open(sys.argv[1], "rb") as inputfile:
    for line in inputfile:
      ### Input needs to be in YUMA format
      ### GPS satellites with IDs 1-32
      ### QZSS satellites with IDs 192-202

      data = [ s.strip() for s in line.decode("utf-8").split(":") ]

      if data[0] == 'ID':
        sat_id = int(data[1])
        almanac[sat_id] = {}
        almanac[sat_id]['skip'] = True
        almanac[sat_id]['id'] = sat_id

        if sat_id >= 1 and sat_id <= 32:
          almanac[sat_id]['skip'] = False
          almanac[sat_id]['sat_type'] = 'GPS'
          almanac[sat_id]['msgId'] = 0x00
          almanac[sat_id]['svId'] = sat_id
          almanac[sat_id]['e_ref'] = 0.0
          almanac[sat_id]['I_ref'] = 0.30 # from IS-GPS-200

        elif sat_id >= 193 and sat_id <= 202:
          almanac[sat_id]['skip'] = False
          almanac[sat_id]['sat_type'] = 'QZSS'
          almanac[sat_id]['msgId'] = 0x05
          almanac[sat_id]['svId'] = sat_id - 193 + 1
          if almanac[sat_id]['svId'] <= 5:
            # From IS-QZSS-PNT-004
            almanac[sat_id]['e_ref'] = 0.06 # semicircles
            almanac[sat_id]['I_ref'] = 0.25
          else:
            # From IS-QZSS-PNT-004
            almanac[sat_id]['e_ref'] = 0.0 # semicircles
            almanac[sat_id]['I_ref'] = 0.0
            # Geosynchronous QZSS not supported in UBX message spec
            almanac[sat_id]['skip'] = True

      elif data[0] == 'Health':
        almanac[sat_id]['svHealth'] = int(data[1])

      elif data[0] == 'Eccentricity':
        # UBX scaling: 2^-21
        eccentricity_abs = float(data[1])
        eccentricity_relative = eccentricity_abs - almanac[sat_id]['e_ref']
        almanac[sat_id]['e'] = int(eccentricity_relative / 2**-21)

      elif data[0] == 'week':
        week = int(float(data[1]))
        almanac[sat_id]['gpsWeek'] = week
        almanac[sat_id]['almWNa'] = week % 256

      elif data[0] == 'Time of Applicability(s)':
        # UBX scaling: 2^12
        # UBX unit: s
        almanac[sat_id]['toa'] = int(float(data[1]) / 2**12)

      elif data[0] == 'Orbital Inclination(rad)':
        # UBX scaling: 2^-19
        # UBX unit: semi-circles
        # Input: YUMA format, direct measurement of inclination angle
        # Output: SEM format, relative to 0.30 semicircles
        inclination_abs = float(data[1]) / math.pi
        inclination_relative = inclination_abs - almanac[sat_id]['I_ref']
        almanac[sat_id]['deltaI'] = int(inclination_relative / 2**-19)

      elif data[0] == 'Rate of Right Ascen(r/s)':
        # UBX scaling: 2^-38
        # UBX unit: semi-circles/s
        almanac[sat_id]['omegaDot'] = int(float(data[1]) / 2**-38 / math.pi)

      elif data[0] == 'SQRT(A)  (m 1/2)':
        # UBX scaling: 2^-11
        # UBX unit: m^0.5
        almanac[sat_id]['sqrtA'] = int(float(data[1]) / 2**-11)

      elif data[0] == 'Right Ascen at Week(rad)':
        # UBX scaling: 2^-23
        # UBX unit: semi-circles
        almanac[sat_id]['omega0'] = int(float(data[1]) / 2**-23 / math.pi)

      elif data[0] == 'Argument of Perigee(rad)':
        # UBX scaling: 2^-23
        # UBX unit: semi-circles
        almanac[sat_id]['omega'] = int(float(data[1]) / 2**-23 / math.pi)

      elif data[0] == 'Mean Anom(rad)':
        # UBX scaling: 2^-23
        # UBX unit: semi-circles
        almanac[sat_id]['m0'] = int(float(data[1]) / 2**-23 / math.pi)

      elif data[0] == 'Af0(s)':
        # UBX scaling: 2^-20
        # UBX unit: s
        almanac[sat_id]['af0'] = int(float(data[1]) / 2**-20)

      elif data[0] == 'Af1(s/s)':
        # UBX scaling: 2^-38
        # UBX unit: s/s
        almanac[sat_id]['af1'] = int(float(data[1]) / 2**-38)

  out = b''

  for sat_id in almanac:
    if not almanac[sat_id]['skip']:
      ubx_gps_alm_length = 36
      header = struct.pack('<BBBBH', 0xb5, 0x62, 0x13, almanac[sat_id]['msgId'],
                          ubx_gps_alm_length)
      payload = struct.pack('<BBBBHBBhhIiiihhI',
                            0x02,
                            0x00,
                            almanac[sat_id]['svId'],
                            almanac[sat_id]['svHealth'],
                            almanac[sat_id]['e'],
                            almanac[sat_id]['almWNa'],
                            almanac[sat_id]['toa'],
                            almanac[sat_id]['deltaI'],
                            almanac[sat_id]['omegaDot'],
                            almanac[sat_id]['sqrtA'],
                            almanac[sat_id]['omega0'],
                            almanac[sat_id]['omega'],
                            almanac[sat_id]['m0'],
                            almanac[sat_id]['af0'],
                            almanac[sat_id]['af1'],
                            0)
      print("-------")
      print("Converted UBX-MGA almanac for %s satellite ID %d." %
              ( almanac[sat_id]['sat_type'], almanac[sat_id]['id']))
      frame = header + payload + ubx_checksum(header[2 : ] + payload)

      # Validate frame
      msg = UBXReader.parse(frame, validate=True, msgmode=SET)
      print(msg)

      out = out + frame

  with open(sys.argv[2], "wb") as outputfile:
    outputfile.write(out)
