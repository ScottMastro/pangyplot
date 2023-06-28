import gzip
from data.model.annotation import Annotation

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
    result["start"] = cols[3]
    result["end"] = cols[4]
    result["info"] = cols[8]

    for c in result["info"].split(";"):
        if c.startswith("ID"):
            result["id"] = c.split("=")[1]
        if c.startswith("gene"):
            result["gene"] = c.split("=")[1]
        if c.startswith("exon_number"):
            result["exon"] = c.split("=")[1]
    
    return result

def parse_gff3(db, gff3, count_update):
    count = 0

    with get_reader(gff3) as file:
        for line in file:
            row = parse_line(line)

            if row:
                row["aid"] = row["id"]
                row["id"] = count
                count += 1
                annotation = Annotation(row)
                db.session.add(annotation)

                count += 1
                count_update(count)
    
        db.session.commit()