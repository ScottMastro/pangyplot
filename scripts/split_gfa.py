import argparse
import gzip
import os

def openfn(file):
    if file.endswith('.gz'):
        open_fn = gzip.open
    else:
        open_fn = open
    return open_fn

def find_P_lines(gfa, prefix):

    chromosomes = dict()

    fn = openfn(gfa)

    with fn(gfa, 'rt') as file:
        for line in file:
            if line.startswith('P'):
                cols = line.strip().split("\t")
                path = cols[2].split(",")

                clean_path = set()
                for node in path:
                    n = node.strip("+-")
                    clean_path.add(n)

                #chromosomes[cols[1]] = clean_path
                #return chromosomes
            if line.startswith('L'):
                cols = line.strip().split("\t")

                print(line)


def separate_lines(gfa, chromosomes):
    
    fn = openfn(gfa)

    with fn(gfa, 'rt') as file:
        for line in file:
            if line.startswith('S'):
                cols = line.strip().split("\t")

                for chr in chromosomes:
                    if cols[1] in chromosomes[chr]:
                        print(cols)

def main():
    parser = argparse.ArgumentParser(description="Splits a gfa file into chromosomes")
    parser.add_argument('gfa', help='Path to a GFA file.')
    parser.add_argument('chr_prefix', help='Prefix for chromosome lines.')

    args = parser.parse_args()

    if not os.path.exists(args.gfa):
        print(f"File does not exist: {args.gfa}")
        return

    chromosomes = find_P_lines(args.gfa, args.chr_prefix)

    separate_lines(args.gfa, chromosomes)


if __name__ == "__main__":
    main()