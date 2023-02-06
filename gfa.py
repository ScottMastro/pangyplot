import gfapy

GFA="./static/data/DRB1-3123_sorted.gfa"
TSV="./static/data/DRB1-3123_sorted.tsv"


def test():

    gfa = gfapy.Gfa.from_file(GFA)
    print(len(gfa.lines))
    b = gfa.line("4")
    b.disconnect()
    print(gfa.segment_names)
    #for line in gfa.lines: 
    #    print(line[1])
