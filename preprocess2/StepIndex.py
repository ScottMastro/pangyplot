import bisect
from collections import defaultdict

class StepIndex:
    def __init__(self, segment_dict, path):
        self.starts = []
        self.ends = []
        self.ranges = defaultdict(list)
        self._step_to_segment = []

        seg_lengths = {sid: segment["length"] for sid,segment in segment_dict.items()}

        pos = 1
        for i,step in enumerate(path["path"]):
            orient = step[-1]
            sid = int(step[:-1])
            length = seg_lengths[sid]
            self.starts.append(pos)
            self.ends.append(pos + length -1)
            
            self.ranges[sid].append(i)
            self._step_to_segment.append(sid)

            pos += length

    def __getitem__(self, seg_id):
        if seg_id not in self.ranges:
            return []
        return self.ranges[seg_id]

    def get_segment(self, step):
        if step < 0 or step >= len(self._step_to_segment):
            return None
        return self._step_to_segment[step]

    def query_bp(self, bp_position):
        i = bisect.bisect_right(self.starts, bp_position) - 1
        i = max(i, 0)
        return (i, self.starts[i], self.ends[i])
    
    def query(self, start, end, debug=False):
        res1 = self.query_bp(start)
        res2 = self.query_bp(end)
        if debug:
            print(f"""[DEBUG] Position query results {start}-{end}. 
                  START: step={res1[0]} / ref coords {res1[1]}-{res1[2]} / nodes {self._step_to_segment[res1[0]]}
                  END:   step={res2[0]} / ref coords {res2[1]}-{res2[2]} / nodes {self._step_to_segment[res2[0]]}""")
        return (res1[0],res2[0])
