(function () {
  const dmcFunctions = window.dashMantineFunctions || {};
  window.dashMantineFunctions = dmcFunctions;

  const dmc = window.dash_mantine_components;
  const iconify = window.dash_iconify;

  dmcFunctions.renderRoundOption = function ({ option, checked }) {
    return React.createElement(
      dmc.Flex,
      { gap: 'xs', className: `round-option ${ checked ? 'selected' : 'unselected' }` },
      React.createElement('div', { className: 'round-number' }, `Round ${ option.value }`),
      React.createElement('div', { className: 'round-overview' }, option.detail),
    );
  };
})();
