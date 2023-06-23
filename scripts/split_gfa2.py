import argparse
import gzip
import os

def separate_lines(gfa):
    
    if gfa.endswith('.gz'):
        open_fn = gzip.open
    else:
        open_fn = open

    counter=1

    header = "" ; firstLine = True
    Sline=True

    base_path = os.path.dirname(gfa)
    out = open(gfa + "_split" + str(counter) + ".gfa", 'w')

    with open_fn(gfa, 'rt') as file:
    

        for line in file:
            if firstLine:
                firstLine = False
                header = line
                out.write(header)
                continue

            if line[0] != "S" and Sline:
                Sline=False
            if line[0] == "S" and not Sline:
                counter+=1
                out = open(gfa + "_split" + str(counter) + ".gfa", 'w')
                out.write(header)
                Sline=True
            
            out.write(line)

def main():
    parser = argparse.ArgumentParser(description="Splits a gfa file into chromosomes")
    parser.add_argument('gfa', help='Path to a GFA file.')

    args = parser.parse_args()

    if not os.path.exists(args.gfa):
        print(f"File does not exist: {args.gfa}")
        return

    header = separate_lines(args.gfa)


if __name__ == "__main__":
    main()