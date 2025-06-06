document.addEventListener('DOMContentLoaded', function () {
  const graph = document.getElementById('us-map');
  if (!graph) return;

  graph.on('plotly_hover', function() {
    graph.style.cursor = 'pointer';
  });

  graph.on('plotly_unhover', function() {
    graph.style.cursor = 'default';
  });
});
