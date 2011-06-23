import json
import csv

"""
Opens a BJCP-supplied CSV file containing style definitions,
parses style definition data, and converts it into a reusable JSON format.

XLS data available at:

http://www.bjcp.org/stylecenter.php
http://www.bjcp.org/docs/2008StyleChart.xls
"""

json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')

reader = csv.reader(open('style.csv', 'rb'))

styles = []

def gravity(val):

    try:
        min, max = val.split('-')
    except ValueError:
        return None, None

    if max > 2:
        max = round(1 + (float(max) / 1000.00), 3)

    return float(min), float(max)

def split(val):
    try:
        min, max = val.split('-')
    except ValueError:
        return None, None

    return float(min), float(max)

f = open('styles.js', 'wb')

for r in reader:
    name, og, fg, abv, ibu, srm = r

    # normalize the name
    name = name.split(' ', 1)[1]

    # normalize the gravities
    min_og, max_og = gravity(og)
    min_fg, max_fg = gravity(fg)

    # normalize abv
    min_abv, max_abv = split(abv) 

    # normalize ibu
    min_ibu, max_ibu = split(ibu)
    if min_ibu and max_ibu:
        min_ibu, max_ibu = int(min_ibu), int(max_ibu)

    # normalize srm
    min_srm, max_srm = split(srm)
    if min_srm and max_srm:
        min_srm, max_srm = int(min_srm), int(max_srm)

    record = {
        'name'      : name,
        'min_og'    : min_og,
        'max_og'    : max_og,
        'min_fg'    : min_fg,
        'max_fg'    : max_fg,
        'min_abv'   : min_abv,
        'max_abv'   : max_abv,
        'min_ibu'   : min_ibu,
        'max_ibu'   : max_ibu,
        'min_srm'   : min_srm,
        'max_srm'   : max_srm
    }

    styles.append(record)

f.write(json.dumps(styles, indent=1))
f.close()
