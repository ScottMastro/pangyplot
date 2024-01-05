function getFormattedDateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;
}

document.getElementById('download-image-button').addEventListener('click', function() {
    const canvas = document.querySelector('.force-graph-container canvas');
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }

    const dateTimeStr = getFormattedDateTime();
    const dataUrl = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = `pangyplot_${dateTimeStr}.png`;
    link.href = dataUrl;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});