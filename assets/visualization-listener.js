function cancelEvent(evt) {
  evt.stopPropagation();
  return false;
}

(function(){
  const id = 'insight-visualization-figure';

  function attachIfReady(){
    const el = document.getElementById(id);
    if (el) {
      // Using a named function will only add the listener once
      el.addEventListener('click', cancelEvent);
      return true;
    }
    
    return false;
  }

  if (!attachIfReady()) {
    // watch the DOM and attach as soon as the element appears
    const mo = new MutationObserver((mutations, obs) => {
      // Cancelling observer when true doesn't seem to work, so we just check each time
      attachIfReady();
    });
    mo.observe(document.body, { childList: true, subtree: true });
  }
})();
