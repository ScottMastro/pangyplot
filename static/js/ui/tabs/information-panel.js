var fullSequence ="";
function updateGraphInfo(nodeid) {
    //todo: avoid using this directly
    nodeInfo = getNodeInformation(nodeid);
    document.getElementById('info-node-id').textContent = nodeInfo.id || '';
    document.getElementById('info-node-type').textContent = nodeInfo.type || '';
    document.getElementById('info-chromosome').textContent = nodeInfo.chrom || '';
    document.getElementById('info-start').textContent = nodeInfo.start || '';
    document.getElementById('info-end').textContent = nodeInfo.end || '';
    document.getElementById('info-length').textContent = nodeInfo.length || '';

    goToNeo4jBrowser(nodeInfo.type, nodeInfo.id)

    fullSequence = nodeInfo.sequence || '';
    const truncatedSequence = fullSequence.slice(0, 10);
    let seq = truncatedSequence + (fullSequence.length > 10 ? '...' : '');
    document.getElementById('info-sequence').textContent = seq;


    if ('subtype' in nodeInfo) {
      document.getElementById('info-subtype').textContent = nodeInfo.subtype;
    } else {
      document.getElementById('info-subtype').textContent = '';
    }

    if ('size' in nodeInfo) {
      document.getElementById('info-size').textContent = nodeInfo.size;
    } else {
      document.getElementById('info-size').textContent = '';
    }

    if ('n' in nodeInfo) {
      document.getElementById('info-number-inside').textContent = nodeInfo.n;
    } else {
      document.getElementById('info-number-inside').textContent = '';
    }
  }
  
document.getElementById('info-copy-sequence').addEventListener('click', function() {
  navigator.clipboard.writeText(fullSequence).then(() => {
      console.log('Sequence copied to clipboard');
  }).catch(err => {
      console.error('Error copying text: ', err);
  });
});

let frameTimes = [];
//average across last [maxFrames] frames
const maxFrames = 10;

function calculateFPS(){
  const elementFPS = document.getElementById('info-fps');

  const now = Date.now();
  frameTimes.push(now);

  if (frameTimes.length > maxFrames) {
      frameTimes.shift();
  }

  if (frameTimes.length > 1) {
      const timeDiff = frameTimes[frameTimes.length - 1] - frameTimes[0];
      const frameRate = 1000 * frameTimes.length / timeDiff;

      elementFPS.textContent = `${frameRate.toFixed(2)}`;
  }
}

function showGraphInfo(graphData){
  const elementNodes = document.getElementById('info-graph-nodes');
  const elementLinks = document.getElementById('info-graph-links');
 
  elementNodes.textContent = `${graphData.nodes.length}`;
  elementLinks.textContent = `${graphData.links.length}`;

}

function goToNeo4jBrowser(nodetype, id) {
  if (!nodetype || !id) {
    console.warn('nodetype and id are required to generate the Neo4j query.');
    return;
  }

  const type = nodetype.charAt(0).toUpperCase() + nodetype.slice(1);
  const query = `MATCH (n:${type}) WHERE n.id = "${id}" RETURN n`;
  const encodedQuery = encodeURIComponent(query);
  const neo4jUrl = `http://localhost:7474/browser/?cmd=edit&arg=${encodedQuery}`;

  const button = document.getElementById('info-neo4j-link');
  if (!button) {
    return;
  }

  button.onclick = () => {
    window.open(neo4jUrl, '_blank');
  };
}


function debugInformationUpdate(graphData){
  calculateFPS();
  showGraphInfo(graphData);
}

function showCoordinates(coordinates){
  const elementCanvasCoord = document.getElementById('info-canvas-coordinates');
  const elementScreenCoord = document.getElementById('info-screen-coordinates');
  const ndigits = 0;

  const x = Math.round(coordinates.x*(10**ndigits))/(10**ndigits);
  const y = Math.round(coordinates.y*(10**ndigits))/(10**ndigits);

  elementCanvasCoord.textContent = `(${x}, ${y})`;

  const mx = Math.round(coordinates.screen.x*100)/100
  const my = Math.round(coordinates.screen.y*100)/100

  elementScreenCoord.textContent = `(${mx}, ${my})`;  
}
