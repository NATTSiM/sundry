#!/usr/bin/env python

import argparse
import csv
import numpy as np

argparser = argparse.ArgumentParser()
argparser.add_argument('-g', '--gather', type=str,
    default='/var/log/gather.out')
args = argparser.parse_args()

def checkPath(path):
	try:
		open(path)
		return path
	except IOError:
		print "Error : gather.out file not found."
		path = raw_input("Enter path to gather.out file : ")
		path = checkPath(str(path))
		return path

path = checkPath(str(args.gather))

# Read all data from gather.out
	# Line 1 should be headers
	# Last line should contain gather data
with open(path) as f:
    reader = csv.reader(f, delimiter="\t")
    d = list(reader)

# Account for line 1 headers
samples = len(d)-1

# Insert ledgerAge into a numpy array
ledgerAge = np.zeros(samples)
for r in range(samples):
	ledgerAge[r] = int(d[r+1][5])

# Display histogram data (arbitrary upper bound)
histogram = np.histogram(ledgerAge, bins=[0,25,60,100000])
binOut = histogram[0]

print
print str(100.0*(float(binOut[0])/samples)) + "% ledger age < 20 seconds"
print str(100.0*(float(binOut[1])/samples)) + "% 20 seconds < ledger age < 60 seconds"
print str(100.0*(float(binOut[2])/samples)) + "% ledger age > 60 seconds\n"


