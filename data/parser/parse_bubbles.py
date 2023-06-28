import json
from data.model.bubble import Bubble,BubbleInside

def process_line(line):

    result = []
    sb = None if "parent_sb" not in line else line["parent_sb"]
    pc = None if "parent_chain" not in line else line["parent_chain"]
    chain_id = line["chain_id"]

    for bubble in line["bubbles"]:
        row = dict()
        row["id"] = bubble["id"]
        row["sb"] = sb
        row["pc"] = pc
        row["chain_id"] = chain_id
        row["type"] = bubble["type"]
        row["start"] = bubble["ends"][0]
        row["end"] = bubble["ends"][1]
        
        row["inside"] = []
        for inside_id in bubble["inside"]:
            inside_row = dict()
            inside_row["id"] = inside_id
            inside_row["bubble_id"] = bubble["id"]
            row["inside"].append(inside_row)

        result.append(row)

    return result

def parse_bubbles(db, jsonFile, count_update):
    count = 0

    with open(jsonFile) as f:
        file = json.load(f)

    for id in file:
        rows = process_line(file[id])
        for row in rows:
            db.session.add(Bubble(row))
            
            for inside_row in row["inside"]:
                db.session.add(BubbleInside(inside_row))

            count += 1
            count_update(count)
    
    db.session.commit()
