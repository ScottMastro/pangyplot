import os

CHR_LIST = []
CYTOBANDS = []
ORGANISM=None

COLOR_MAP = {
    "acen": "#CC0000",
    "gneg": "#FFFFFF",
    "gpos100": "#000000",
    "gpos25": "#CCCCCC",
    "gpos50": "#7F7F7F",
    "gpos75": "#333333",
    "gvar": "#0DCC00",
    "stalk": "#00CC83"
}

def set_cytoband(organism, cytoband=None, canonical=None):
    global ORGANISM, CHR_LIST, CYTOBAND_DICT

    organism_to_genome = {
        "human": "hg38",
        "dog": "canFam3",
        "mouse": "mm39",
        "fruitfly": "dm6",
        "zebrafish": "danRer11",
        "chicken": "galGal6",
        "rabbit": "oryCun2"
    }
    
    if not cytoband:
        genome = organism_to_genome.get(organism)
        if genome:
            ORGANISM=organism
            script_dir = os.path.dirname(os.path.realpath(__file__))
            cytoband = os.path.join(script_dir, "static", "cytoband", f"{genome}.cytoBand.txt")
            canonical = os.path.join(script_dir, "static", "cytoband", f"{genome}.canonical.txt")

    # Load chromosome list
    CHR_LIST = []
    if canonical:
        with open(canonical, 'r') as f:
            CHR_LIST = [line.strip() for line in f if line.strip()]

    # Load and parse cytoband data
    CYTOBAND_DICT = {}
    noncanonical = set()
    if cytoband:
        with open(cytoband, 'r') as file:
            for line in file:
                chr, start, end, name, band_type = line.strip().split("\t")
                if name == "":
                    name = chr
                if chr not in CHR_LIST:
                    continue

                start = int(start)
                end = int(end)
                color = COLOR_MAP.get(band_type, "#000000")

                if chr not in CYTOBAND_DICT:
                    CYTOBAND_DICT[chr] = []

                band = {
                    "band": len(CYTOBAND_DICT[chr]),
                    "start": start,
                    "end": end,
                    "name": name,
                    "type": band_type,
                    "color": color,
                    "chr": chr
                }
                CYTOBAND_DICT[chr].append(band)

        # Normalize sizes and positions
        for chr in CYTOBAND_DICT:
            total_size = max(b["end"] for b in CYTOBAND_DICT[chr])
            for band in CYTOBAND_DICT[chr]:
                band["size"] = (band["end"] - band["start"]) / total_size
                band["x"] = band["start"] / total_size

def get_cytoband(chromosome=None):
    if chromosome:
        return {"chromosome": CYTOBAND_DICT.get(chromosome, [])}
    else:
        return {"chromosome": CYTOBAND_DICT, "order": CHR_LIST, "organism" : ORGANISM}

def get_canonical():
    return CHR_LIST