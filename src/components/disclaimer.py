from dash import dcc

disclaimer = dcc.Markdown('''
    The US COVID-19 Scenario Modeling Hub aims to produce robust projections to provide real-time actionable modeling
    evidence to support ongoing public health needs and decision-making. For Round 19, eight teams contributed both national
    and state-specific projections of the trajectory of COVID-19 during April 27, 2025 to April 25, 2026. Detailed scenario
    descriptions and setting assumptions are provided on the SMH GitHub site. See covid19scenariomodelinghub.org for more
    results and details.
  ''', style=dict(color='gray'))
