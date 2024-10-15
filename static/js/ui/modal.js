function setupModal(modalId, openButtonId, closeButtonId, onByDefault) {
    let modal = document.getElementById(modalId);
    let openModalButton = document.getElementById(openButtonId);
    let closeModalButton = document.getElementById(closeButtonId);

    if (onByDefault){
        modal.style.display = "block";
    } else{
        modal.style.display = "none";
    }
    if (openModalButton) {
        openModalButton.onclick = function() {
            modal.style.display = "block";
        };
    }

    if (closeModalButton) {
        closeModalButton.onclick = function() {
            modal.style.display = "none";
        };
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };

    // Optional: Close the modal with the Escape key
    window.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && modal.style.display === "block") {
            modal.style.display = "none";
        }
    });
}