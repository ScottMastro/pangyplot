let RIGHT_CLICK_MANAGER = null;

class RightClickManager {
    constructor(forceGraph) {
      this.graphData = forceGraph.graphData();
      this.options = [];
      this.menuElement = this.createMenuElement();
    }
  
    createMenuElement() {
      const menu = document.createElement('div');
      menu.classList.add('custom-context-menu');
      document.body.appendChild(menu);
      return menu;
    }
  
    addOption(iconName, labelText, category, onClickFunction) {
        this.options.push({ iconName, labelText, category, onClickFunction });
      }

    showMenu(x, y) {
        this.menuElement.innerHTML = '';
        const targetNodes = [];

        this.graphData.nodes.forEach(node => {
            if (node.isSelected){
                targetNodes.push(node);
            }
        });

      console.log(targetNodes.length,targetNodes )
      const categorizedOptions = this.categorizeOptions();

      if (categorizedOptions['general']) {
        this.addLabel('Actions:');
        categorizedOptions['general'].forEach(option => this.addOptionToMenu(option));
      }

      if (targetNodes.length > 0 && categorizedOptions['node']) {
        this.addLabel('Highlighted node actions:');
        categorizedOptions['node'].forEach(option => this.addOptionToMenu(option, targetNodes));
      }

      if (!this.menuElement.innerHTML.trim()) {
        return;
      }
  
      // Position menu
      this.menuElement.style.left = `${x}px`;
      this.menuElement.style.top = `${y}px`;
      this.menuElement.style.display = 'block';
    }
  
    categorizeOptions() {
        const categories = {};
        this.options.forEach((option) => {
          if (!categories[option.category]) {
            categories[option.category] = [];
          }
          categories[option.category].push(option);
        });
        return categories;
    }
    
    addLabel(text) {
        const label = document.createElement('div');
        label.classList.add('context-menu-category-label');
        label.textContent = text;
        this.menuElement.appendChild(label);
    }

    hideMenu() {
      this.menuElement.style.display = 'none';
    }
  
    addOptionToMenu(option, targetObject=null) {
        const row = document.createElement('div');
        row.classList.add('context-menu-row');
    
        const icon = document.createElement('i');
        icon.classList.add('fa', `fa-${option.iconName}`);
    
        const label = document.createElement('span');
        label.textContent = option.labelText;
    
        row.appendChild(icon);
        row.appendChild(label);
    
        row.addEventListener('click', (e) => {
          e.stopPropagation();
          option.onClickFunction(targetObject);
          this.hideMenu();
        });
    
        this.menuElement.appendChild(row);
      }
}

function rightClickManagerSetup(forceGraph){
    RIGHT_CLICK_MANAGER = new RightClickManager(forceGraph);

      RIGHT_CLICK_MANAGER.addOption('burst', 'Pop nodes', 'node', (nodes) => {
        popNodeEnginePopAll(nodes, forceGraph)
      });

    RIGHT_CLICK_MANAGER.addOption('dna', 'Show Sequence', 'node', (nodes) => {        
      const nchar= 25;
      
      nodes.forEach(node => {
          let nodeInfo = getNodeInformation(node.nodeid);
          let fullSequence = nodeInfo.sequence;
          let truncatedSequence = fullSequence.slice(0, nchar);
          let seq = truncatedSequence + (fullSequence.length > nchar ? '...' : '');
          node.label = seq || "";
        });
      });
      
      RIGHT_CLICK_MANAGER.addOption('pen', 'Add Custom Label', 'node', (nodes) => {
        const label = prompt("Enter a custom label for the nodes:");
        if (label) {
      
          nodes.forEach(node => {
            node.label = label;
          });
        }
      });

      RIGHT_CLICK_MANAGER.addOption('trash-can', 'Clear Labels', 'node', (nodes) => {
        nodes.forEach(node => {
          node.label = null;
        });
      });

      RIGHT_CLICK_MANAGER.addOption('lock-open', 'Unlock nodes', 'node', (nodes) => {
        nodes.forEach(node => {
          node.fx = null;
          node.fy = null;
        });     
      });

      RIGHT_CLICK_MANAGER.addOption('arrows-to-circle', 'Recenter Graph', 'general', () => {
        forceGraph.zoomToFit(200, 10, node => true);
      });
      
      RIGHT_CLICK_MANAGER.addOption('download', 'Download Image', 'general', () => {
        downloadGraphImage()
      });
      

    
    return RIGHT_CLICK_MANAGER;

}