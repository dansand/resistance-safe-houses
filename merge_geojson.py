# -*- coding: utf-8 -*-
from json import load, JSONEncoder
import json
from optparse import OptionParser
from re import compile
import glob
import os

###########################################
#Remove any files not 'close' to Melbourne
###########################################
files = glob.glob("geojsons/*.geojson")
for fname in files:
    with open(fname) as f:
        data = json.load(f)
        lon = data['features'][0]['geometry']['coordinates'][0]
        lat = data['features'][0]['geometry']['coordinates'][1]
        if (-45 < lat < 35) and (142 < lon < 150):
            print(fname,"okay")
        else:
            print(fname, "bad")
            os.remove(fname)


###########################################
#Merge Jsons
###########################################

float_pat = compile(r'^-?\d+\.\d+(e-?\d+)?$')
charfloat_pat = compile(r'^[\[,\,]-?\d+\.\d+(e-?\d+)?$')

parser = OptionParser()

defaults = dict(precision=6)

parser.set_defaults(**defaults)

parser.add_option('-p', '--precision', dest='precision',
                  type='int', help='Digits of precision, default %(precision)d.' % defaults)



options, args = parser.parse_args()
outfile = "merged.geojson"

try:
    os.remove(outfile)
except OSError:
    pass

infiles = glob.glob("geojsons/*.geojson")

outjson = dict(type='FeatureCollection', features=[])

for infile in infiles:
    injson = load(open(infile))

    if injson.get('type', None) != 'FeatureCollection':
        raise Exception('Sorry, "%s" does not look like GeoJSON' % infile)

    if type(injson.get('features', None)) != list:
        raise Exception('Sorry, "%s" does not look like GeoJSON' % infile)

    outjson['features'] += injson['features']

encoder = JSONEncoder(separators=(',', ':'))
encoded = encoder.iterencode(outjson)

format = '%.' + str(options.precision) + 'f'
output = open(outfile, 'w')

for token in encoded:
    if charfloat_pat.match(token):
        # in python 2.7, we see a character followed by a float literal
        output.write(token[0] + format % float(token[1:]))

    elif float_pat.match(token):
        # in python 2.6, we see a simple float literal
        output.write(format % float(token))

    else:
        output.write(token)
