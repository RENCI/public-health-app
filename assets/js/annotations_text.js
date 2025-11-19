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
      label.style.textShadow = `-0.05ex 0 0 black, 0.05ex 0 0 black`;
    });
  }

  function clearHighlight(labelEls) {
    labelEls.forEach(label => {
            label.style.textShadow = '';
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
