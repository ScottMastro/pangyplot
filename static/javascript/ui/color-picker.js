function applyGradient(color1, color2, color3) {
    let gradient;
    let useMiddle = true;
    if (color1 == color2 || color3 == color2){
        useMiddle = false;
    }
    if (useMiddle) {
        gradient = `linear-gradient(to right, ${color1}, ${color2}, ${color3})`;
    } else {
        gradient = `linear-gradient(to right, ${color1}, ${color3})`;
    }
    document.getElementById('gradient-display').style.background = gradient;
}

document.querySelectorAll('.node-color-picker').forEach(picker => {
    picker.addEventListener('change', () => {
        const color1 = document.getElementById('color1').value;
        const color2 = document.getElementById('color2').value;
        const color3 = document.getElementById('color3').value;
        unselectAllButtons("preset-color-button-container")
        applyGradient(color1, color2, color3);
    });
});

function updateColorPickers(color1, color2, color3) {
    document.getElementById('color1').value = color1;
    document.getElementById('color2').value = color2;
    document.getElementById('color3').value = color3;
}
document.querySelectorAll('.preset-color').forEach(elem => {
    elem.addEventListener('click', () => {
        const color1 = elem.getAttribute('data-color1');
        const color2 = elem.getAttribute('data-color2');
        const color3 = elem.getAttribute('data-color3');
        updateColorPickers(color1, color2, color3);
        applyGradient(color1, color2, color3);
    });
});

let defaultChoice = document.getElementsByClassName('preset-color option-button-selected')[0];
if (defaultChoice) {
    let color1 = defaultChoice.getAttribute('data-color1');
    let color2 = defaultChoice.getAttribute('data-color2');
    let color3 = defaultChoice.getAttribute('data-color3');

    applyGradient(color1, color2, color3);
    updateColorPickers(color1, color2, color3);
}

document.getElementById('link-color').value = "#969696";
document.getElementById('bg-color').value = "#101020";