

document.getElementById('go-button').addEventListener('click', function() {
    console.log('Button was clicked!');
});

function updateGoValues(chromValue = null, startValue = null, endValue = null) {
    if (chromValue !== null) {
        document.getElementById('go-chrom').textContent = chromValue;
    }
    if (startValue !== null) {
        document.getElementById('go-start').textContent = startValue;
    }
    if (endValue !== null) {
        document.getElementById('go-end').textContent = endValue;
    }
}

function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}

document.getElementById('go-chrom-start-end').addEventListener('click', function() {
    const chrom = document.getElementById('go-chrom').textContent;
    const start = document.getElementById('go-start').textContent;
    const end = document.getElementById('go-end').textContent;
    const textToCopy = chrom + ':' + start + '-' + end;

    copyToClipboard(textToCopy);
    showCopySuccess();
});

const goCopyEffectWaitTime = 400;
let showGoCopyEffect = true;
function showCopySuccess() {
    if (showGoCopyEffect){
        const div = document.getElementById('go-chrom-start-end');
        div.style.backgroundColor = 'var(--highlight)';
        
        showCopyPopup();

        showGoCopyEffect = false;
        setTimeout(() => {
            showGoCopyEffect = true;
        }, goCopyEffectWaitTime);

        setTimeout(() => {
            div.style.backgroundColor = '';
            div.style.color = '';
        }, 200);
    }
}

function showCopyPopup() {
    const popup = document.createElement('div');
    popup.textContent = 'Copied!';
    popup.id = 'copyPopup';
    document.body.appendChild(popup);

    const area = document.getElementById('go-chrom-start-end');
    const areaRect = area.getBoundingClientRect();
    popup.style.position = 'absolute';
    popup.style.left = `${areaRect.left}px`;
    popup.style.top = `${window.scrollY + areaRect.top - 30}px`;
    
    setTimeout(() => {
        popup.style.opacity = '0';
        setTimeout(() => document.body.removeChild(popup), 500);
    }, 800);
}