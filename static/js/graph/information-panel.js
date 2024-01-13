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