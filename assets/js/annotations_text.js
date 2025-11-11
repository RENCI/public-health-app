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

  function setGlow(labelEls, color) {
    labelEls.forEach(label => {
      label.style.filter = `drop-shadow(0 0 3px ${color})`;
    });
  }

  function clearGlow(labelEls) {
    labelEls.forEach(label => {
      label.style.filter = '';
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
      const glowColor = labels?.[0]?.style?.fill || 'crimson';
      setGlow(labels, glowColor);
    });

    el.addEventListener('mouseleave', () => {
      const labels = getChartLabelsFor(el);
      clearGlow(labels);
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
