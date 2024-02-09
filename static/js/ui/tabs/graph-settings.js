document.addEventListener('DOMContentLoaded', function () {
    const sliders = [
        { id: "friction-slider", defaultValue: 0.0228 },
        { id: "velocity-slider", defaultValue: 0.4 },
        { id: "other1-slider", defaultValue: 0.2 },
        { id: "other2-slider", defaultValue: 0.3 },
        { id: "other3-slider", defaultValue: 0.5 },
        { id: "other4-slider", defaultValue: 0.6 }
    ];

    sliders.forEach(sliderInfo => {
        const slider = document.getElementById(sliderInfo.id);
        const output = document.getElementById(`${sliderInfo.id}-value`);
        const resetButton = document.querySelector(`button[onclick="resetSlider('${sliderInfo.id}', ${sliderInfo.defaultValue})"]`);

        updateResetButtonColor(slider, sliderInfo.defaultValue, resetButton);

        slider.oninput = function() {
            output.innerHTML = this.value;
            updateResetButtonColor(this, sliderInfo.defaultValue, resetButton);
        };
    });

    window.resetSlider = function(sliderId, defaultValue) {
        const slider = document.getElementById(sliderId);
        const output = document.getElementById(`${sliderId}-value`);
        const resetButton = document.querySelector(`button[onclick="resetSlider('${sliderId}', ${defaultValue})"]`);

        slider.value = defaultValue;
        output.innerHTML = defaultValue;
        updateResetButtonColor(slider, defaultValue, resetButton);
    };

    function updateResetButtonColor(slider, defaultValue, resetButton) {
        if (parseFloat(slider.value) === defaultValue) {
            resetButton.classList.remove("reset-button-modified");
            resetButton.classList.add("reset-button-default");
        } else {
            resetButton.classList.remove("reset-button-default");
            resetButton.classList.add("reset-button-modified");
        }
    }

    document.getElementById('reset-all-button').addEventListener('click', function() {
        sliders.forEach(sliderInfo => {
            resetSlider(sliderInfo.id, sliderInfo.defaultValue);
        });
    });
});
