from app import db
import sys
import gzip

from model.annotation import Annotation

def add_row_to_annotations(i, line):
    cols = line.strip().split("\t")
    infoCols = cols[8].split(";")

    id = None ; gene = None ; exon = None

    for c in infoCols:
        if c.startswith("ID"):
            id = c.split("=")[1]
        if c.startswith("gene"):
            gene = c.split("=")[1]
        if c.startswith("exon_number"):
            exon = c.split("=")[1]

    new_row = Annotation(i=i, annotationId=id, chrom=cols[0], start=cols[3], end=cols[4],
                             source=cols[1], type=cols[2], gene=gene, info=cols[8])
    db.session.add(new_row)



def populate_annotations(app, gff3):
    count = 0

    def do_line(line, count):
        if line.startswith("#"):
            return count
    
        count += 1
        add_row_to_annotations(count, line)
        if count % 1000 == 0:
            sys.stdout.write('L')
            sys.stdout.flush()
            db.session.commit()
        return count

    with app.app_context():

        if gff3.endswith(".gz"):
            with gzip.open(gff3, 'rt') as f:
                for line in f:
                    count = do_line(line, count)
        else:
            with open(gff3) as f:
                for line in f:
                    count = do_line(line, count)

        db.session.commit()