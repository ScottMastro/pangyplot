function buildUrl(base, params) {
    return `${base}?${Object.entries(params).map(([key, value]) => `${key}=${value}`).join('&')}`;
}

function fetchData(url, logLabel = '') {
    return fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: during ${logLabel}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(logLabel, data);
            return data;
        })
        .catch(error => {
            console.error(`There was a problem with ${logLabel}:`, error);
        });
}

function findNearestNode(nodes, coordinates) {
    let nearestNode = null;
    let minDistance = Infinity;
    
    nodes.forEach(node => {
        const distance = Math.sqrt((coordinates.x - node.x) ** 2 + (coordinates.y - node.y) ** 2);
        // give a boost to smaller nodes
        const effectiveDistance = distance*(node.isSingleton ? 0.9 : 1);

        if (effectiveDistance < minDistance) {
            minDistance = effectiveDistance;
            nearestNode = node;
        }
    });

    return nearestNode;
}

function findNormalizedDistance(a, b, canvas) {
    const normX = canvas.max.x - canvas.min.x;
    const normY = canvas.max.y - canvas.min.y

    const normDistX = (b.x - canvas.min.x)/normX - (a.x - canvas.min.x)/normX
    const normDistY = (b.y - canvas.min.y)/normY - (a.y - canvas.min.y)/normY

    //in units relative to the size of the canvas
    return Math.sqrt((normDistX) ** 2 + (normDistY) ** 2);
}

function showLoader() {
    document.querySelector('.loader').style.display = 'block';
    //document.querySelector('.loader-filter').style.display = 'block';
}

function hideLoader() {
    document.querySelector('.loader').style.display = 'none';
    document.querySelector('.loader-filter').style.display = 'none';
}
hideLoader()

function findBoundingBoxNodes(nodes) {
    let xmin = Infinity;
    let xmax = -Infinity;
    let ymin = Infinity;
    let ymax = -Infinity;

    nodes.forEach(node => {
        if (node.x < xmin) xmin = node.x;
        if (node.x > xmax) xmax = node.x;
        if (node.y < ymin) ymin = node.y;
        if (node.y > ymax) ymax = node.y;
    });

    return {
        x: (xmin + xmax) / 2,
        y: (ymin + ymax) / 2,
        xmin: xmin,
        xmax: xmax,
        ymin: ymin,
        ymax: ymax
    };
}