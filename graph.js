fetch('/home/scott/projects/graph_viz/graph_viz/data')
  .then(response => response.text())
  .then(text => console.log(text))

d3.tsv("/home/scott/projects/graph_viz/graph_viz/data", function(data) {
    // use data here
});
