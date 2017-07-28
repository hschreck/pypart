import argparse
import os
import sys
import re

"""Argument Parser
Accepts device, geometry, and primary arguments"""
parser = argparse.ArgumentParser()
parser.add_argument('--device', help='Specify block device to create partition table for (defaults to /dev/sda)', default="/dev/sda")
parser.add_argument('--geometry', help='Specify sfpart geometry file (defaults to $PWD/sda-pt.sf)', default=f"{os.getcwd()}/sda-pt.sf")
parser.add_argument('--primary', help='Specify primary (resized) partition (defaults to 2)', default=2)
parser.add_argument('--size', help='Override size of --device')

args = parser.parse_args()
blockDevice = args.device.replace("/dev/", "")

"""Get the number of sectors on the disk"""
diskSectors = open(f"/sys/block/{blockDevice}/size").read().rstrip()
if args.size is not None:
    diskSectors = int(args.size)

with open(args.geometry) as geometryFile:
    geometry = [line.rstrip() for line in geometryFile]

def getPartitionSize(partitionLine):
    return int(re.search(r"size= *\d*", partitionLine).group().replace("size=", ""))

def getPartitionStart(partitionLine):
    return int(re.search(r"start= *\d*", partitionLine).group().replace("start=", ""))

if int(diskSectors) < (getPartitionSize(geometry[-1]) + getPartitionStart(geometry[-1])):
    sys.exit("Oops!  Looks like the disk you're trying to make this for is too small!")

lineIndex = -1

partEnd = int(diskSectors)

while True:
    geoLine = geometry[lineIndex]
    if f"{args.device}{args.primary}" in geoLine:
        break
    else:
        partStart = partEnd - getPartitionSize(geoLine)
        geometry[lineIndex] = re.sub(r"start= *\d*", f"start= {partStart}", geoLine)
        partEnd = partStart
        lineIndex -= 1

geometry[lineIndex] = re.sub(r"size= *\d*", f"size= {partEnd - getPartitionStart(geometry[lineIndex])}", geometry[lineIndex])


for line in geometry:
    print(line)

