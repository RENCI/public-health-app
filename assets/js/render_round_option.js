(function () {
  const dmcFunctions = window.dashMantineFunctions || {};
  window.dashMantineFunctions = dmcFunctions;

  const dmc = window.dash_mantine_components;
  const iconify = window.dash_iconify;

  dmcFunctions.renderRoundOption = function ({ option, checked }) {
    const checkedIcon = React.createElement(iconify.DashIconify, {
      icon: 'feather:check',
      width: 16,
    });

    return React.createElement(
      dmc.Flex,
      { gap: 'xs', class: 'round-option' },
      React.createElement('div', { class: 'round-number' }, `Round ${ option.value }`),
      React.createElement('div', { class: 'round-details' }, option.detail),
    );
  };
})();
