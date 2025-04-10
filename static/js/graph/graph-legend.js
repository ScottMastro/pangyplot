function createLegendContainer() {
    let legend = document.getElementById('graph-legend');
    if (!legend) {
      legend = document.createElement('div');
      legend.id = 'graph-legend';
      legend.style.display = 'none'; // hidden until used
      document.getElementById('graph-container').appendChild(legend);
    }
  
    // Ensure there's a title element
    if (!document.getElementById('graph-legend-title')) {
      const title = document.createElement('div');
      title.id = 'graph-legend-title';
      title.style.fontWeight = 'bold';
      title.style.marginBottom = '6px';
      legend.appendChild(title);
    }
  }
  
  function setLegendTitle(title) {
    createLegendContainer();
    const titleDiv = document.getElementById('graph-legend-title');
    if (title) {
      titleDiv.textContent = title;
      titleDiv.style.display = 'block';
    } else {
      titleDiv.style.display = 'none';
    }
  }
  
  function setLegendItems(items) {
    createLegendContainer();
    const legend = document.getElementById('graph-legend');
  
    // Remove old items but keep the title
    while (legend.children.length > 1) {
      legend.removeChild(legend.lastChild);
    }
  
    if (items.length === 0) {
      legend.style.display = 'none';
      return;
    }
  
    legend.style.display = 'block';
  
    items.forEach(item => {
      const div = document.createElement('div');
      div.className = 'legend-item';
  
      const colorBox = document.createElement('span');
      colorBox.className = 'legend-color';
      colorBox.style.backgroundColor = item.color;
  
      const label = document.createElement('span');
      label.textContent = item.label;
  
      div.appendChild(colorBox);
      div.appendChild(label);
      legend.appendChild(div);
    });
  }
  
  function clearLegend() {
    const legend = document.getElementById('graph-legend');
    if (legend) {
      legend.style.display = 'none';
      // remove all children except the title
      while (legend.children.length > 1) {
        legend.removeChild(legend.lastChild);
      }
    }
  }
  