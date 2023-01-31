CYTOBAND_FILE="./static/annotations/cytoBand_hg38.txt"

SIZE="size"
BAND="band"
START="start"
X="x"
END="end"
NAME="name"
TYPE="type"
COLOR="color"

# "acen" is centromeric; 
# "stalk" refers to the short arm of acrocentric chromosomes chr13,14,15,21,22; 
# "gvar" bands tend to be heterochomatin, either pericentric or telomeric.
COLOR_MAP = { "acen": "#CC0000",
              "gneg": "#FFFFFF",
              "gpos100": "#000000",
              "gpos25": "#CCCCCC",
              "gpos50":"#7F7F7F",
              "gpos75":"#333333",
              "gvar": "#0DCC00",
              "stalk": "#00CC83" }

def get_cytoband(chromosome=None):

    bandDict = dict()

    with open(CYTOBAND_FILE) as file:

        for line in file.readlines():
            chr, start, end, name, type = line.split("\t")
            type = type.strip()
            start=int(start); end=int(end)

            if not chromosome is None:
                if chr != chromosome: continue 

            color = COLOR_MAP[type]
            if chr not in bandDict:
                bandDict[chr] = []

            band = len(bandDict[chr])
            INFO=[BAND, START, END, NAME, TYPE, COLOR]
            info = [band, start, end, name, type, color]

            bandDict[chr].append( {k: v for k,v in zip(INFO, info)} )

    for chr in bandDict:
        totalSize = max([band[END] for band in bandDict[chr]])
        for i,band in enumerate(bandDict[chr]):
            bandDict[chr][i][SIZE] = (band[END]-band[START])/totalSize
            bandDict[chr][i][X] = band[START]/totalSize

    return bandDict