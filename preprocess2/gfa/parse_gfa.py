import sys
import gzip
from preprocess2.StepIndex import write_step_index
from preprocess2.gfa.parse_segments import parse_segments
from preprocess2.gfa.parse_links import parse_links
from preprocess2.gfa.parse_paths import parse_paths

def get_reader(gfa_file):
    if gfa_file.endswith(".gz"):
        return gzip.open(gfa_file, 'rt')
    return open(gfa_file)

def verify_reference(ref_path, matching_refs):
    if len(matching_refs) == 0:
        print(f"   ❌ ERROR: Reference sample '{ref_path}' not found in any sample IDs.")
        sys.exit(1)
    elif len(matching_refs) > 1:
        print(f"   ❌ ERROR: Reference sample string '{ref_path}' matched multiple samples:")
        for name in matching_refs:
            print(f"     - {name}")
        print("   Please provide a more specific reference name.")
        sys.exit(1)

    print(f"   🎯 Found reference path {matching_refs[0]}.")

def parse_gfa(gfa_file, ref_path, layout_coords, dir):
    print("➡️ Parsing GFA.")

    # ==== PATHS ====
    print("   🧵 Gathering paths from GFA...", end="", flush=True)
    path_info, reference_info = parse_paths(get_reader(gfa_file), ref_path)
    sample_idx, path_dict = path_info
    reference_path, matching_refs = reference_info
    verify_reference(ref_path, matching_refs)
    print(" Done.")

    # ==== SEGMENTS ====
    print("   🍡 Gathering segments from GFA...", end="", flush=True)
    segment_dict = parse_segments(get_reader(gfa_file), layout_coords, dir)
    print(" Done.")
    
    write_step_index(segment_dict, reference_path, dir)

    # ==== LINKS ====
    print("   🧷 Gathering links from GFA...", end="", flush=True)
    link_dict = parse_links(get_reader(gfa_file), sample_idx, path_dict, dir)
    print(" Done.")

    return segment_dict, link_dict
