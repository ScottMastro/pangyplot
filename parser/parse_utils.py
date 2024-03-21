
def parse_reference_string(str, ref=None):

    if "|" in str:
        chrom = str.split("|")[-1]
        genome = str.split("|")[0]
        if genome.startswith("id="):
            genome = genome[3:]
    elif "#" in str:
        genome = str.split("#")[0]
        chrom = str.split("#")[-1]
    else:
        genome = ref
        chrom = str

    return {"chrom": chrom, "genome": genome}
