function slugify(str) {
  return String(str)
    .normalize('NFKD') // split accented characters into their base characters and diacritical marks
    .replace(/[\u0300-\u036f]/g, '') // remove all the accents, which happen to be all in the \u03xx UNICODE block.
    .trim() // trim leading or trailing whitespace
    .toLowerCase() // convert to lowercase
    .replace(/[^a-z0-9 -]/g, '') // remove non-alphanumeric characters
    .replace(/\s+/g, '-') // replace spaces with hyphens
    .replace(/-+/g, '-'); // remove consecutive hyphens
}

(function() {
  function getChartLabelsFor(el) {
    const idToMatch = slugify(el.dataset.annotationRef);
    const annotationTextElements = Array.from(document.querySelectorAll('.annotation-text'))
      .filter(label => idToMatch == slugify(label.dataset.unformatted));

    return annotationTextElements;
  }

  function setHighlight(labelEls) {
    labelEls.forEach(label => {
      const parent = label.parentNode;
      const existing = parent.querySelector('rect.annotation-bg');

      // avoid duplicates
      if (!existing) {
        const bbox = label.getBBox();

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.classList.add('annotation-bg');

        const padding = 4; // around the text

        rect.setAttribute('x', bbox.x - padding);
        rect.setAttribute('y', bbox.y - padding);
        rect.setAttribute('width', bbox.width + padding * 2);
        rect.setAttribute('height', bbox.height + padding * 2);
        rect.setAttribute('rx', 4);
        rect.setAttribute('ry', 4);

        // use annotation color OR default
        const bgColor = label.style.fill || label.getAttribute('fill') || '#ddd';
        rect.setAttribute('fill', bgColor);
        rect.setAttribute('opacity', 0.25);

        // insert behind text
        parent.insertBefore(rect, label);
      }
    });
  }

  function clearHighlight(labelEls) {
    labelEls.forEach(label => {
      const parent = label.parentNode;
      const rect = parent.querySelector('rect.annotation-bg');
      if (rect) rect.remove();
    });
  }

  function styleAnnotationReference(el) {
    const newStyle = {
      cursor: 'pointer',
      textDecoration: 'underline',
      textDecorationStyle: 'dashed',
      textDecorationColor: el.style.color || 'inherit',
      textUnderlineOffset: '5px',
    };
    Object.assign(el.style, newStyle);
  }

  function attachAnnotationEvents(el) {
    el.addEventListener('mouseenter', () => {
      const labels = getChartLabelsFor(el);
      setHighlight(labels);
    });

    el.addEventListener('mouseleave', () => {
      const labels = getChartLabelsFor(el);
      clearHighlight(labels);
    });
  }

  window.attachAnnotationListeners = function() {
    const annotations = document.querySelectorAll('.annotation-text');

    document.querySelectorAll('[data-annotation-ref]').forEach(el => {
      if (el._hasListener) return;
      styleAnnotationReference(el);
      attachAnnotationEvents(el);
      el._hasListener = true;
    });
  };
})();
