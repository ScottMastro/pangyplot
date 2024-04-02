import sys
import gzip

def parse_mappings(filename):
    open_func = gzip.open if filename.endswith('.gz') else open
    mappings = {}
    with open_func(filename, 'rt') as f:  # 'rt' mode for reading text from potentially compressed files
        for line in f:
            original, replacement = line.strip().split(' ')
            mappings[original] = replacement
    return mappings

def replace_in_column(text, mappings):
    parts = text.split('<')
    for i, part in enumerate(parts):
        if '>' in part:
            before, after = part.split('>', 1)
            parts[i] = '<' + mappings.get(before, before) + '>' + after
    return ''.join(parts)

def process_file(data_file, mappings_file):
    mappings = parse_mappings(mappings_file)
    open_func = gzip.open if data_file.endswith('.gz') else open
    
    with open_func(data_file, 'rt') as file:  # 'rt' mode for reading text
        for line in file:
            columns = line.strip().split(' ')
            if len(columns) >= 5:
                columns[4] = replace_in_column(columns[4], mappings)
            print(' '.join(columns))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py data_file(.gz) mappings_file(.gz)")
        sys.exit(1)
    
    data_file_path = sys.argv[1]
    mappings_file_path = sys.argv[2]
    
    process_file(data_file_path, mappings_file_path)
