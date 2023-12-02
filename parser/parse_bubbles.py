import json
from db.insert.insert_bubble import insert_bubbles, add_bubble_properties
from db.insert.insert_chain import insert_chains, add_chain_properties
from db.modify.graph_modify import add_null_nodes, connect_bubble_ends_to_chain, add_chain_subtype

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
    
    insert_bubbles(bubbles)
    insert_chains(chains)
    add_null_nodes()
    add_bubble_properties()
    add_chain_properties()
    connect_bubble_ends_to_chain()
    add_chain_subtype()