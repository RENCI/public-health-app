(function () {
  const dmcFunctions = window.dashMantineFunctions || {};
  window.dashMantineFunctions = dmcFunctions;

  const dmc = window.dash_mantine_components;
  const iconify = window.dash_iconify;

  dmcFunctions.renderRoundOption = function ({ option, checked }) {
    const words = {
      19: 'Nineteen',
    };

    const checkedIcon = React.createElement(iconify.DashIconify, {
      icon: 'feather:check',
      width: 16,
    });

    return React.createElement(
      dmc.Group,
      { spacing: 'xs' },
      React.createElement('div', {}, words[option.value] || option.value),
      React.createElement('span', {}, option.label),
      checked ? checkedIcon : null
    );
  };
})();
