import json
import db.neo4j_db as neo4jdb

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
        row["inside"] = bubble["inside"]

        result.append(row)

    return result

def parse_bubbles(jsonFile):
    with open(jsonFile) as f:
        data = json.load(f)

    chains = []
    bubbles = []
    for chainId in data:
        chainData = data[chainId]
        sb = None if "parent_sb" not in chainData else chainData["parent_sb"]
        pc = None if "parent_chain" not in chainData else chainData["parent_chain"]

        chain = {"id": chainData["chain_id"], 
                 "ends": chainData["ends"],
                 "sb": sb, "pc": pc,
                 "bubbles":[x["id"] for x in chainData["bubbles"]]}
        chains.append(chain)
        bubbles.extend(chainData["bubbles"])
    
    neo4jdb.add_bubbles(bubbles)
    neo4jdb.add_chains(chains)
    neo4jdb.add_null_nodes()
    neo4jdb.add_bubble_properties()
    neo4jdb.connect_bubble_ends_to_chain()
    neo4jdb.add_chain_complexity()