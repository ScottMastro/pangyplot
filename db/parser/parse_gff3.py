import gzip,os
from db.insert_annotation import add_annotations

def get_reader(gff3):
    if gff3.endswith(".gz"):
        return gzip.open(gff3, 'rt')
    return open(gff3)

def parse_line(line):

    if line.startswith("#"):
        return None
    
    result = dict()
    cols = line.strip().split("\t")
    
    result["chrom"] = cols[0]
    result["source"] = cols[1]
    result["type"] = cols[2]
    result["start"] = int(cols[3])
    result["end"] = int(cols[4])
    #result["info"] = cols[8]

    result["id"] = None
    result["gene"] = None
    result["exon"] = None

    for c in cols[8].split(";"):
        if c.startswith("ID"):
            result["id"] = c.split("=")[1]
        elif c.startswith("gene_name"):
            result["gene"] = c.split("=")[1]
        elif c.startswith("exon_number"):
            result["exon"] = int(c.split("=")[1])
        else:
            result[c.split("=")[0]] = c.split("=")[1]
    return result

def parse_gff3(gff3):
    
    annotations = []
    filename = os.path.basename(gff3)
    with get_reader(gff3) as file:
        for line in file:
            annotation = parse_line(line)
            if annotation:
                annotation["file"] = filename
                annotations.append(annotation)
    add_annotations(annotations)
