(function () {
  window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
      async capture_thumbnail(n) {
        if (!n) return window.dash_clientside.no_update;

        const plot = document.querySelector('#graph .js-plotly-plot');

        if (!plot) {
          console.warn('nothing found with selector "#graph .js-plotly-plot"');
          return window.dash_clientside.no_update;
        }

        try {
          const img = await Plotly.toImage(plot, {
            format: 'png',
            width: 1000,
            height: 800,
            scale: 2,
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
