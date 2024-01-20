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

    fullSequence = nodeInfo.sequence || '';
    const truncatedSequence = fullSequence.substr(0, 10);
    let seq = truncatedSequence + (fullSequence.length > 10 ? '...' : '');
    document.getElementById('info-sequence').textContent = seq;

    if ('subtype' in nodeInfo) {
        document.getElementById('optional-subtype').style.display = 'block';
        document.getElementById('info-subtype').textContent = nodeInfo.subtype;
      } else {
        document.getElementById('optional-subtype').style.display = 'none';
      }

      if ('size' in nodeInfo) {
        document.getElementById('optional-size').style.display = 'block';
        document.getElementById('info-size').textContent = nodeInfo.size;
      } else {
        document.getElementById('optional-size').style.display = 'none';
      }

    
      if ('n' in nodeInfo) {
        document.getElementById('optional-number-inside').style.display = 'block';
        document.getElementById('info-number-inside').textContent = nodeInfo.n;
      } else {
        document.getElementById('optional-number-inside').style.display = 'none';
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
const maxFrames = 100;
const elementFPS = document.getElementById('frames-per-second');

function calculateFPS(){
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

const elementGraphCoord = document.getElementById('graph-coordinates');
const elementMouseCoord = document.getElementById('mouse-coordinates');

function showCoordinates(coordinates){
  const x = Math.round(coordinates.x*100)/100
  const y = Math.round(coordinates.y*100)/100

  elementGraphCoord.textContent = `(${x}, ${y})`;

  const mx = Math.round(coordinates.screen.x*100)/100
  const my = Math.round(coordinates.screen.y*100)/100

  elementMouseCoord.textContent = `(${mx}, ${my})`;

  
}
