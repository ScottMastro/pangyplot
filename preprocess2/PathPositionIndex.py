import bisect

class PathPositionIndex:
    def __init__(self, segment_dict, path):
        seg_lengths = {sid: segment["length"] for sid,segment in segment_dict.items()}

        self.seg_ids = []
        self.starts = []
        self.ends = []

        pos = 0
        for step in path["path"]:
            orient = step[-1]
            sid = int(step[:-1])

            length = seg_lengths[sid]
            self.seg_ids.append(sid)
            self.starts.append(pos)
            self.ends.append(pos + length)
            pos += length +1

    def query_bp(self, bp_position):
        i = bisect.bisect_right(self.starts, bp_position) - 1
        i = max(i, 0)
        return (self.seg_ids[i], self.starts[i], self.ends[i])
    
    def query(self, start, end, debug=False):
        res1 = self.query_bp(start)
        res2 = self.query_bp(end)
        if debug:
            print(f"""[DEBUG] Position query results {start}-{end}. 
                  START: node {res1[0]} / ref coords {res1[1]}-{res1[2]}
                  END:   node {res2[0]} / ref coords {res2[1]}-{res2[2]}""")
        return (res1[0],res2[0])
