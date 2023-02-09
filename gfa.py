import gfapy
import subprocess

GFATOOLS="/home/scott/bin/gfatools/gfatools"

GFA="./static/data/chr18.smooth.final.gfa"
TSV="./static/data/chr18.smooth.final.tsv"


def test(chr, start, end):
    region = chr + "-" + str(start) + ":" + str(end)

    result = subprocess.run([GFATOOLS, "view", GFA, "-R", region], capture_output=True, text=True).stdout.strip("\n")
    print(result)
    
    print("result")

    gfa = gfapy.Gfa.from_file(GFA)
    print(len(gfa.lines))
    b = gfa.line("4")
    b.disconnect()
    print(gfa.segment_names)
    #for line in gfa.lines: 
    #    print(line[1])
