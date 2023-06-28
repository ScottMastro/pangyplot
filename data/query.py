from segment import SimpleSegment,SimpleBubble

from model.segment import Segment
from model.link import Link
from model.annotation import Annotation
from model.bubble import Bubble,BubbleInside

def get_nodes(graph, chr=None, start=None, end=None):
    rows = Segment.query.all()
    for row in rows:
        node = SimpleSegment(row.nodeid, description="desc", size=3,
        chrom=row.chrom, pos=row.pos, length=len(row.seq))
        node.add_source_node(row.x1, row.y1)
        node.add_sink_node(row.x2, row.y2)
        graph[row.nodeid] = node

    return graph

def get_edges(graph, chr=None, start=None, end=None):
    rows = Link.query.all()
    for row in rows:
        fromNode = graph[row.from_id]
        toNode = graph[row.to_id]
        fromNode.add_link_to(toNode)
        toNode.add_link_from(fromNode)

    return graph

def get_annotations(annotations, chromosome, start, end):

    rows = Annotation.query.filter(
        Annotation.chrom == chromosome,
        Annotation.start >= start,
        Annotation.end <= end
    ).all()
    
    for row in rows:
        d = {"index": row.id, "id": row.aid, "chrom": row.chrom, "start": row.start, "end": row.end,
        "type": row.type, "info": row.info}  
        annotations.append(d)

    return annotations


def get_bubbles(graph, chr=None, start=None, end=None):
    
    rows = Bubble.query.all()

    for row in rows:
        
        bid = "bubble_" + str(row.id)
        inside = BubbleInside.query.filter_by(bubble_id=row.id).all()

        subgraph = []
        for e in inside:
            subgraph.append(graph[e.node_id])

        bubbles[bid] = SimpleBubble(bid, graph[row.start], graph[row.end], subgraph, 
                description="desc", size=5)

    return bubbles


'''

def get_nodes(graph):
    return query.get_nodes(graph)
def get_edges(graph):
    return query.get_edges(graph)
def get_bubbles(bubbles, graph):
    return query.get_bubbles(bubbles, graph)
def get_annotations(annotations, chromosome, start, end):
    return query.get_annotations(annotations, chromosome, start, end)


## ============================================================
## helpers
## ============================================================

def drop(app, tablename):

    with app.app_context():

        connection = db.engine.connect()
        metadata = db.MetaData(bind=db.engine)
        your_table = db.Table(tablename, metadata, autoload=True)
        your_table.drop(connection)
        db.session.commit()
        connection.close()


def drop_all(app):
    drop(app, "link")
    drop(app, "segment")
    drop(app, "bubble")
    drop(app, "chain")
    drop(app, "bubble_inside")
    #drop(app, "annotation")


def populate_all(app, gfa, tsv, bubble, gff3):
    gfa.populate_gfa(app, gfa)
    tsv.populate_tsv(app, tsv)
    json.populate_bubbles(app, bubble)
    #gff3.populate_annotations(app, gff3)

'''