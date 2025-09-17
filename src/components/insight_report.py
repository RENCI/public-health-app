from dash import dcc
import dash_mantine_components as dmc

from ..data.round19 import insights


insight_report = dcc.Markdown(f'''
  ## Executive Summary Report
  _Round completed: June 4, 2025_

  In the 19th Round of COVID-19 scenario projections, the US COVID-19 Scenario
  Modeling Hub aimed to estimate the impact of three vaccine recommendation
  levels for the 2025-26 season: i) no recommendation, resulting in minimal
  vaccine coverage; ii) high-risk group recommendation, including individuals
  over 65 years and those under 65 years with high-risk conditions; and iii)
  universal recommendation for all eligible age groups, each with uptake
  corresponding to 2024-25 coverage levels.

  ## Rationale

  Even the best models of emerging infections struggle to give accurate
  forecasts at time scales greater than 3-4 weeks due to unpredictable drivers
  such as a changing policy environment, behavior change, the development of
  new control measures, and stochastic events. However, policy decisions around
  the course of emerging infections often require projections in the time frame
  of months. The goal of long-term projections is to compare outbreak
  trajectories under different scenarios, as opposed to offering a specific,
  unconditional estimate of what “will” happen.

  As such, long-term projections can guide longer-term decision-making while
  short-term forecasts are more useful for situational awareness and guiding
  immediate response. The need for long-term epidemic projections is
  particularly acute in a severe pandemic, such as COVID-19, that has a large
  impact on the economy; for instance, economic and budget projections require
  estimates of outbreak trajectories in the 3-6 month time scale.
''')
