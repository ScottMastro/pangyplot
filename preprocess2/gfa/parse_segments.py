import preprocess2.gfa.data_structures.SegmentIndex as db

def parse_line_S(line):
    segment = dict()
    cols = line.strip().split("\t")
    segment["id"] = int(cols[1])
    seq = cols[2].upper()
    segment["seq"] = seq
    segment["gc_count"] = seq.count('G') + seq.count('C')
    segment["n_count"] = seq.count('N')
    segment["length"] = len(seq)
    return segment

def parse_segments(gfa, layout_coords, dir):
    conn = db.create_segment_table(dir)
    cur = conn.cursor()
    segment_dict = dict()

    counter = 0
    for line in gfa:
        if line[0] == "S":
            segment_info = parse_line_S(line)

            for xy in ["x1", "y1", "x2", "y2"]:
                segment_info[xy] = layout_coords[counter][xy]

            db.insert_segment(cur, segment_info)
            segment_dict[segment_info["id"]] = segment_info
            counter += 1

    conn.commit()
    conn.close()
    
    return segment_dict
