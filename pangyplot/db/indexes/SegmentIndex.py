from array import array
import db.sqlite.segment_db as db

class SegmentIndex:
    def __init__(self, chr_dir):
        self.conn = db.get_connection(chr_dir)
        self.cur = self.conn.cursor()

        self.id = array('I')
        self.length = array('I')
        self.x1 = array('f')
        self.y1 = array('f')
        self.x2 = array('f')
        self.y2 = array('f')

        for row in db.load_segments():
            sid = row["id"]
            self.length[sid] = row["length"]
            self.x1[sid] = row["x1"]
            self.y1[sid] = row["y1"]
            self.x2[sid] = row["x2"]
            self.y2[sid] = row["y2"]

    def __getitem__(self, seg_id):
        return db.get_segment(self.cur, seg_id)
    
    def get_by_ids(self, seg_ids):
        return [db.get_segment(self.cur, seg_id) for seg_id in seg_ids if seg_id < len(self.id)]

    def get_between(self, start_id, end_id):
        return db.get_segment_range(self.cur, start_id, end_id)

