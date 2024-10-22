import re

def process_gfa_line(line):
    if line.startswith("P"):
        # Extract the path part
        parts = line.split("\t")
        path = parts[1]
        
        # Split the ID by #
        id_parts = path.split("#")
        print(id_parts)
        
        if len(id_parts) <=3:
            return line
        
        # Extract relevant sections from the path
        genome_part = "#".join(id_parts[:2]) # Keep the first two parts (e.g., "CHM13#0")
        chr_part = id_parts[2].split("_")[0]  # Get the "chr7" part
        num_start = int(id_parts[2].split("_")[1])  # Get the first number (start)
        
        # Find the [start-end] part using regex
        match = re.search(r"\[(\d+)-(\d+)\]", path)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            
            # Adjust by adding the start value to the range
            
            new_start = num_start + start
            new_end = num_start + end
            
            # Build the new path by replacing the #0[ with [
            new_path = f"{genome_part}#{chr_part}[{new_start}-{new_end}]"
            new_line = f"{parts[0]}\t{new_path}\t" + "\t".join(parts[2:])
            
            return new_line
    return line

def process_gfa_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            processed_line = process_gfa_line(line)
            outfile.write(processed_line)

input_gfa = 'in.gfa'
output_gfa = 'out.gfa'

process_gfa_file(input_gfa, output_gfa)

