(function() {
  window.attachAnnotationListeners = function() {
    document.querySelectorAll('.chart-annotation-text').forEach(el => {
      if (!el._hasListener) {
        el.addEventListener('mouseenter', () => {
          const textContent = el.textContent.trim();
          
          const glowColor = el.style.color || 'crimson';

          // find chart labels where data-unformatted is contained in the textContent
          const chartLabels = Array.from(document.querySelectorAll('.annotation-text'))
            .filter(label => textContent.includes(label.dataset.unformatted));
          
          
          chartLabels.forEach(label => {
            label.style.filter = `drop-shadow(0 0 3px ${ glowColor })`;
          });
        });

        el.addEventListener('mouseleave', () => {
          const textContent = el.textContent.trim();
          
          const chartLabels = Array.from(document.querySelectorAll('.annotation-text'))
            .filter(label => textContent.includes(label.dataset.unformatted));
          
          chartLabels.forEach(label => {
            label.style.filter = '';
          });
        });
          
        el._hasListener = true;
      }
    });
  };
})();
