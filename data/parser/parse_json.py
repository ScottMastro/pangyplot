from app import db
import sys
import json

from model.chain import Chain
from model.bubble import Bubble
from model.bubble_inside import BubbleInside

def populate_bubbles(app, jsonFile):
    count = 0

    with app.app_context():
        with open(jsonFile) as f:
            bubbleJson = json.load(f)

            for bubbleId in bubbleJson:
                c = bubbleJson[bubbleId]
                
                sb = None if "parent_sb" not in c else c["parent_sb"]
                pc = None if "parent_chain" not in c else c["parent_chain"]

                new_chain_row = Chain(id=c["chain_id"], start=c["ends"][0], end=c["ends"][1],
                    parent_sb=sb, parent_chain=pc)
                db.session.add(new_chain_row)

                for b in c["bubbles"]:
                    new_bubble_row = Bubble(id=b["id"], chain_id=c["chain_id"], 
                        type=b["type"], start=b["ends"][0], end=b["ends"][1])
                    db.session.add(new_bubble_row)

                    for inside in b["inside"]:
                        new_bubble_inside_row = BubbleInside(id=inside, bubble_id=b["id"])
                        db.session.add(new_bubble_inside_row)

                count = count+1
                if count % 1000 == 0:
                    sys.stdout.write('B')
                    sys.stdout.flush()
                    db.session.commit()
        db.session.commit()

