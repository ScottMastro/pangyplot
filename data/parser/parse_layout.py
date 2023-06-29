import gzip
from data.model.segment import Segment

def get_reader(layout):
    if layout.endswith(".gz"):
        return gzip.open(layout, 'rt')
    return open(layout)

def parse_lines(line1, line2):

    cols1 = line1.strip().split("\t")
    cols2 = line2.strip().split("\t")
    id = int(int(cols1[0])/2)

    result = dict()
    result["id"] = str(id)
    result["x1"] = cols1[1]
    result["y1"] = cols1[2]
    result["x2"] = cols2[1]
    result["y2"] = cols2[2]

    return result

def populate_layout(db, layout, count_update):
    count = 0
    prevLine = None
    skipFirstLine = True

    with get_reader(layout) as file:
        for line in file:
            if skipFirstLine:
                skipFirstLine=False
                continue

            count += 1
            if count % 2 == 0:
                row = parse_lines(prevLine, line)
                if row:
                    segment = Segment.query.get_or_404(row["id"])
                    segment.update_layout(row["x1"], row["y1"], row["x2"], row["y2"])

            prevLine = line
            count_update(count)
                
        db.session.commit()