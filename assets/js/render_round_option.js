(function () {
  const dmcFunctions = window.dashMantineFunctions || {};
  window.dashMantineFunctions = dmcFunctions;

  const dmc = window.dash_mantine_components;
  const iconify = window.dash_iconify;

  dmcFunctions.renderRoundOption = function ({ option, checked }) {
    return React.createElement(
      dmc.Stack,
      { className: `round-option ${ checked ? 'selected' : 'unselected' }` },
      React.createElement(dmc.Group, { justify: 'space-between' }, [
        React.createElement(dmc.Text, { key: 'label', size: 'md', className: 'round-option-label' }, option.label),
        React.createElement(dmc.Text, { key: 'count', size: 'xs' }, `${ option.insights_count } insights`)
      ]),
      React.createElement(dmc.Text, { size: 'sm' }, option.snippet),
      React.createElement(dmc.Text, { key: 'label', size: 'sm', c: 'dimmed', className: 'round-option-sublabel' }, option.sublabel),
    );
  };
})();
