document.addEventListener('DOMContentLoaded', function () {
    const sliders = [
        { id: "collapse-slider", defaultValue: 250 },
        { id: "alpha-slider", defaultValue: 0.0228 },
        { id: "friction-slider", defaultValue: 0.1 },
        { id: "attraction-slider", defaultValue: -500 },
        { id: "collision-slider", defaultValue: 50 },
        { id: "spread-slider", defaultValue: 0 },
        { id: "pull-slider", defaultValue: 100 }
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
