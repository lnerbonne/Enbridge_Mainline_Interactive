#!/bin/sh
set -e
for n in 1 2 3 4 5 6 7 11 14_64 61 62 65 67 78; do
  tippecanoe -q -o data/pmtiles/line$n.pmtiles -l $n -Z0 -z10 --drop-densest-as-needed --force data/geojson/$n.geojson
done
tippecanoe -q -o data/pmtiles/MAINLINE_FULL.pmtiles -l MAINLINE_FULL -Z0 -z10 --drop-densest-as-needed --force data/geojson/MAINLINE_FULL.geojson
