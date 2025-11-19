(function () {
  const selector = '#graph .js-plotly-plot';

  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
      async capture_thumbnail(n) {
        if (!n) return window.dash_clientside.no_update;

        const plot = document.querySelector(selector);

        if (!plot) {
          console.warn(`nothing found with selector "${selector}"`);
          return window.dash_clientside.no_update;
        }

        try {
          const img = await Plotly.toImage(plot, {
            format: 'svg',
            width: 1000,
            height: 800,
            scale: 1,
          });
          return img;
        } catch (error) {
          console.error('Failed to generate thumbnail', error);
          return window.dash_clientside.no_update;
        }
      },
    },
  });
})();
