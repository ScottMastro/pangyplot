import gzip,os
from db.insert.insert_annotation import add_annotations

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

    result["strand"] = cols[6]

    result["id"] = None
    result["gene"] = None
    result["exon"] = None

    for c in cols[8].split(";"):
        if c.lower().startswith("id"):
            result["id"] = c.split("=")[1]
            if result["id"].startswith("exon:"):
                result["exon"] = int(result["id"].split(":")[-1])
        elif c.lower().startswith("parent="):
            result["parent"] = c.split("=")[1]
        elif c.lower().startswith("gene_name"):
            result["gene"] = c.split("=")[1]
        elif c.lower().startswith("exon_number"):
            result["exon"] = int(c.split("=")[1])
        else:
            result[c.split("=")[0].lower()] = c.split("=")[1]
    return result

def add_primary_information(transcript):
    transcript["ensembl_canonical"] = False
    transcript["mane_select"] = False
    if "tag" in transcript:
        tag = transcript["tag"].lower()
        if "ensembl_canonical" in tag:
            transcript["ensembl_canonical"] = True
        if "mane_select" in tag:
            transcript["mane_select"] = True
    return transcript

def split_annotations_by_type(annotations):
    typeDict = {"Gene":[], "Transcript":[], "Exon":[], 
                "CDS":[], "Codon":[], "UTR":[], "Annotation":[]}

    for annotation in annotations:
        if not "type" in annotation:
            typeDict["Annotation"].append(annotation)
        if  "gene" == annotation["type"].lower():
            if "gene_id" in annotation: del annotation["gene_id"]
            typeDict["Gene"].append(annotation)
        elif "exon" == annotation["type"].lower():
            typeDict["Exon"].append(annotation)
        elif "transcript" == annotation["type"].lower():
            if "transcript_id" in annotation: del annotation["transcript_id"]
            annotation = add_primary_information(annotation)
            typeDict["Transcript"].append(annotation)
        elif "cds" == annotation["type"].lower():
            typeDict["CDS"].append(annotation)
        elif "start_codon" == annotation["type"].lower():
            annotation["subtype"] = "start"
            typeDict["Codon"].append(annotation)
        elif "stop_codon" == annotation["type"].lower():
            annotation["subtype"] = "stop"
            typeDict["Codon"].append(annotation)
        elif "five_prime_utr" == annotation["type"].lower():
            annotation["subtype"] = "five_prime"
            typeDict["UTR"].append(annotation)
        elif "three_prime_utr" == annotation["type"].lower():
            annotation["subtype"] = "three_prime"
            typeDict["UTR"].append(annotation)
        else:
            typeDict["Annotation"].append(annotation)

    return typeDict


def parse_gff3(gff3, refGenome):
    
    annotations = []
    filename = os.path.basename(gff3)
    with get_reader(gff3) as file:
        for line in file:
            annotation = parse_line(line)
            if annotation:
                if refGenome is not None:
                    annotation["genome"] = refGenome
                    annotation["chrom"] = annotation['chrom']
                annotation["file"] = filename
                annotations.append(annotation)

    annotationDict = split_annotations_by_type(annotations)
    add_annotations(refGenome, annotationDict)
