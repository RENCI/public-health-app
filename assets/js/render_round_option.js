(function () {
  if (typeof window === "undefined") return;

  window.dashMantineFunctions = window.dashMantineFunctions || {};

  window.dashMantineFunctions.renderRoundOption = function ({ option, checked }) {
    const dmc = window.dash_mantine_components;
    const React = window.React;

    if (!dmc || !React) {
      console.error("dash_mantine_components or React not available");
      return null;
    }

    return React.createElement(
      dmc.Stack,
      { className: `round-option ${checked ? "selected" : "unselected"}` },
      React.createElement(dmc.Group, { justify: "space-between" }, [
        React.createElement(dmc.Text, { key: "label", size: "md", className: "round-option-label" }, option.label),
        React.createElement(dmc.Text, { key: "count", size: "xs" }, `${option.insights_count} insights`),
      ]),
      React.createElement(dmc.Text, { size: "sm" }, option.snippet),
      React.createElement(
        dmc.Text,
        { key: "sublabel", size: "sm", c: "dimmed", className: "round-option-sublabel" },
        option.sublabel,
      ),
    );
  };
})();
