const EMPTY = "⬜";

document.getElementById("go-button").addEventListener("click", function () {
  const goBox = document.getElementById("go-chrom-start-end");
  let chrom = document.getElementById("go-chrom").textContent;
  let start = document.getElementById("go-start").textContent;
  let end = document.getElementById("go-end").textContent;

  if (
    chrom == null || chrom == EMPTY ||
    start == null || start == EMPTY ||
    end == null || end == EMPTY
  ) {
    goBox.classList.add("shake", "error-input");
    goBox.addEventListener(
      "animationend",
      function () {
        goBox.classList.remove("shake");
        goBox.classList.remove("error-input");
      },
      { once: true },
    );
  } else {
    const data = {
      chrom: chrom,
      start: start,
      end: end,
    };
    const selectedEvent = new CustomEvent("constructGraph", { detail: data });
    document.dispatchEvent(selectedEvent);
  }
});

function updateGoValues(chromValue = null, startValue = null, endValue = null) {
  if (chromValue !== null) {
    document.getElementById("go-chrom").textContent = chromValue;
  } else {
    document.getElementById("go-chrom").textContent = EMPTY;
  }
  if (startValue !== null) {
    document.getElementById("go-start").textContent = startValue;
  } else {
    document.getElementById("go-start").textContent = EMPTY;
  }
  if (endValue !== null) {
    document.getElementById("go-end").textContent = endValue;
  } else {
    document.getElementById("go-end").textContent = EMPTY;
  }
}

document.addEventListener("selectedCoordinatesChanged", function (event) {
  updateGoValues(event.detail.chrom, event.detail.start, event.detail.end);
});

function updateGenomicCoordinates(rawText) {
  if (rawText == null || rawText == "") {
    return;
  }
  const textBox = document.getElementById("go-chrom-start-end");
  let input = rawText.replace(/\s+/g, "");

  const pattern = /^(chr)?[^:]+:\d+-\d+$/;

  function errorAnimationBadCoordinates() {
    textBox.classList.add("shake", "error-input");
    textBox.addEventListener(
      "animationend",
      function () {
        textBox.classList.remove("shake");
        textBox.classList.remove("error-input");
      },
      { once: true },
    );
  }

  if (!pattern.test(input)) {
    errorAnimationBadCoordinates();
    return;
  }

  let [chrom, range] = input.split(":");
  let [start, end] = range.split("-").map((s) => parseInt(s, 10));

  if (end < 0 || start < 0) {
    errorAnimationBadCoordinates();
    return;
  }

  if (end < start) {
    errorAnimationBadCoordinates();
    return;
  }

  textBox.value = "";

  const data = {chrom: chrom, start: start, end: end, source: "coordinate-text"};
  document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));
}

function transformToTextbox(elementId) {
  const container = document.getElementById(elementId);

  let input = container.querySelector("input");
  if (!input) {
    const currentInside = container.innerHTML;
    const currentText = container.textContent.replace(/\s+/g, "");

    input = document.createElement("input");
    input.type = "text";
    input.classList.add("editable-textbox");
    if (currentText == `${EMPTY}:${EMPTY}-${EMPTY}`) {
      input.value = "";
    } else {
      input.value = currentText;
    }

    container.innerHTML = "";
    container.appendChild(input);

    input.focus();
    input.select();

    function revertToText() {
      const container = document.getElementById(elementId);
      const userInput = input.value;
      container.innerHTML = currentInside;
      console.log;
      updateGenomicCoordinates(userInput);
    }

    // Modify the transformToTextbox function to include this:
    input.addEventListener("blur", revertToText);
    input.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        revertToText();
      }
    });
  }
}

document.getElementById("go-chrom-start-end").addEventListener("click", function () {
  transformToTextbox("go-chrom-start-end")});
document.getElementById("go-flanking").addEventListener("click", function () {
  transformToTextbox("go-flanking")});
  
function copyToClipboard(text) {
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}

document.getElementById("coordinate-copy-button").addEventListener("click", function () {
  const chrom = document.getElementById("go-chrom").textContent;
  const start = document.getElementById("go-start").textContent;
  const end = document.getElementById("go-end").textContent;
  const textToCopy = chrom + ":" + start + "-" + end;

  copyToClipboard(textToCopy);
  showCopySuccess("go-chrom-start-end");
});

const goCopyEffectWaitTime = 400;
let showGoCopyEffect = true;
function showCopySuccess(elementId) {
  if (showGoCopyEffect) {
    const div = document.getElementById(elementId);
    div.style.backgroundColor = "var(--highlight)";

    showCopyPopup(elementId);

    showGoCopyEffect = false;
    setTimeout(() => {
      showGoCopyEffect = true;
    }, goCopyEffectWaitTime);

    setTimeout(() => {
      div.style.backgroundColor = "";
      div.style.color = "";
    }, 200);
  }
}

function showCopyPopup(elementId) {
  const popup = document.createElement("div");
  popup.textContent = "Copied!";
  popup.id = "copyPopup";
  document.body.appendChild(popup);

  const area = document.getElementById(elementId);
  const areaRect = area.getBoundingClientRect();
  popup.style.position = "absolute";
  popup.style.left = `${areaRect.left}px`;
  popup.style.top = `${window.scrollY + areaRect.top - 30}px`;

  setTimeout(() => {
    popup.style.opacity = "0";
    setTimeout(() => document.body.removeChild(popup), 500);
  }, 800);
}
