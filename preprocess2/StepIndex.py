import os
import bisect
from collections import defaultdict
import gzip
import json

NAME = "step_index.json.gz"

def write_step_index(segments, path, db_dir):
    idx_path = os.path.join(db_dir, NAME)

    starts = []
    ends = []
    ranges = defaultdict(list)
    step_to_segment = []

    pos = 1
    for i, step in enumerate(path["path"]):
        sid = int(step[:-1])
        length = segments[sid]["length"]
        starts.append(pos)
        ends.append(pos + length - 1)
        ranges[sid].append(i)
        step_to_segment.append(sid)
        pos += length

    # Convert defaultdict to regular dict for JSON
    data = {
        "starts": starts,
        "ends": ends,
        "step_to_segment": step_to_segment,
        "ranges": {str(k): v for k, v in ranges.items()}
    }

    with gzip.open(idx_path, 'wt') as f:
        json.dump(data, f)

class StepIndex:
    def __init__(self, db_dir):

        # Initialize empty data
        self.starts = []
        self.ends = []
        self.ranges = defaultdict(list)
        self._step_to_segment = []

        idx_path = os.path.join(db_dir, NAME)
        self._load(idx_path)

    def _load(self, idx_path):
        with gzip.open(idx_path, 'rt') as f:
            data = json.load(f)

        self.starts = data["starts"]
        self.ends = data["ends"]
        self._step_to_segment = data["step_to_segment"]
        self.ranges = defaultdict(list, {int(k): v for k, v in data["ranges"].items()})

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
