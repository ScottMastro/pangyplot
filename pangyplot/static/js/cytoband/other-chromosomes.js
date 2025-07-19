document.addEventListener("DOMContentLoaded", function () {
    const datalist = document.getElementById("cytoband-genome-other-options");
    const inputSelector = document.getElementById("cytoband-genome-other-selector");
    const label = document.getElementById("cytoband-genome-other-selector-label");
  
    function populateOtherChromosomeDropdown(chromosomes) {
      chromosomes.forEach((chromosome) => {
        const option = document.createElement("option");
        option.value = chromosome;
        datalist.appendChild(option);
      });
    }
  
    fetch("/chromosomes?noncanonical=true")
      .then((response) => response.json())
      .then(populateOtherChromosomeDropdown)
      .catch((error) => console.error("Error:", error));
  
    function checkIfOtherChromosomeInDropdown(input) {
      const chrom = input.trim();
      for (let option of datalist.options) {
        let optionValue = option.value.trim();
        if (optionValue === chrom) {
          return true;
        }
      }
      return false;
    }
  
    inputSelector.addEventListener("input", function (event) {
      let chrom = event.target.value;
      if (!checkIfOtherChromosomeInDropdown(chrom)) {
        return;
      }
  
      const data = {chrom: chrom, start: null, end: null, source: "cytoband-other"};
      document.dispatchEvent( new CustomEvent('selectedCoordinatesChanged', { detail: data }));
    });
  
    document.addEventListener("selectedCoordinatesChanged", function (event) {
      if (checkIfOtherChromosomeInDropdown(event.detail.chrom)) {
        inputSelector.value = event.detail.chrom;
        label.classList.add("highlighted");
      } else {
        label.classList.remove("highlighted");
      }
    });
});