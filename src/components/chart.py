from dash import dcc
import pandas as pd
from src.util.data import build_dataset_path, collect_data

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def chart(control_values={}):
  scenarios = [int(s) for s in control_values.get('scenarios', ['13'])]
  models = [int(s) for s in control_values.get('models', [])]
  age_group = control_values.get('age_group', '0-130')
  location = control_values.get('location', 'US')
  target = control_values.get('target', 'incident_hospitalization')
  uncertainty = control_values.get('uncertainty', 'None')
  annotations = control_values.get('annotations', {})

  path = build_dataset_path(round_number=19, location=location, target=target)
  df = pd.DataFrame(collect_data(path))

  # filter by scenario, model, age_group
  if scenarios:
    df = df[df['scenario_id'].isin(scenarios)]
  if models:
    df = df[df['model_name'].isin(models)]
  if age_group:
    df = df[df['age_group'] == age_group]

  # load gold standard data
  gold_std_path = (
    'src/data/rounds/round19/gold_standard/covid_nhsn_hosp_inc.csv'  # path to cleaned CSV
  )
  gold_std_df = pd.read_csv(gold_std_path, parse_dates=['time_value'])

  # filter gold standard to align with controls
  gold_std_df = gold_std_df[
    (gold_std_df['age_group'] == age_group) & (gold_std_df['geo_value_fullname'] == location)
  ]

  # mapping confidence interval value to quantile bounds
  conf_int_map = {
    '50%': [(0.25, 0.75)],
    '95%': [(0.025, 0.975)],
    'Multi': [(0.025, 0.975), (0.05, 0.95), (0.1, 0.9), (0.25, 0.75)],
  }

  # use same color with opacity for all confidence intervals
  conf_int_color = 'rgba(100,100,255,0.25)'

  num_rows = len(scenarios)
  fig = make_subplots(
    rows=num_rows,
    cols=1,
    vertical_spacing=0.1,
    subplot_titles=[f'Scenario {s}' for s in scenarios],
  )
  fig.update_xaxes(matches='x')
  fig.update_yaxes(matches='y')

  for i, scenario in enumerate(scenarios, start=1):
    scenario_df = df[df['scenario_id'] == scenario]

    # add uncertainty intervals
    if uncertainty in conf_int_map:
      for lower_q, upper_q in conf_int_map[uncertainty]:
        lower = scenario_df[scenario_df['type_id'] == lower_q]
        upper = scenario_df[scenario_df['type_id'] == upper_q]

        for model in lower['model_name'].unique():
          lower_model = lower[lower['model_name'] == model]
          upper_model = upper[upper['model_name'] == model]

          fig.add_trace(
            go.Scatter(
              x=pd.concat([lower_model['target_end_date'], upper_model['target_end_date'][::-1]]),
              y=pd.concat([lower_model['value'], upper_model['value'][::-1]]),
              fill='toself',
              fillcolor=conf_int_color,
              line=dict(color='rgba(0,0,0,0)'),
              hoverinfo='skip',
              showlegend=False,
            ),
            row=i,
            col=1,
          )

    # main line for median (0.5 quantile)
    median_df = scenario_df[scenario_df['type_id'] == 0.5]
    for model in median_df['model_name'].unique():
      model_df = median_df[median_df['model_name'] == model]
      fig.add_trace(
        go.Scatter(
          x=model_df['target_end_date'],
          y=model_df['value'],
          mode='lines+markers',
          name=f'Model {model}',
          legendgroup=f'Model {model}',
          showlegend=(i == 1),
        ),
        row=i,
        col=1,
      )

    # gold standard line
    fig.add_trace(
      go.Scatter(
        x=gold_std_df['time_value'],
        y=gold_std_df['value'],
        mode='lines+markers',
        name='Gold standard',
        line=dict(color='rebeccapurple', dash='dot'),
        marker=dict(symbol='diamond'),
        legendgroup='Gold standard',
        showlegend=(i == 1),
      ),
      row=i,
      col=1,
    )

  for line in annotations:
    if line.get('value'):
      line_value = line.get('value')
      line_label = line.get('label', '')
      line_color = line.get('color', '#222222')

      for yaxis_name in fig.select_yaxes():
        fig.add_hline(
          y=line_value,
          line_dash='dot',
          line_color=line_color,
          line_width=1,
          annotation_text=line_label,
          annotation_position='top left',
          annotation_font_color=line_color,
        )

  fig.update_layout(
    hovermode='x unified', height=300 * num_rows, title='Forecast values over time (by scenario)'
  )
  fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor')
  fig.update_yaxes(showspikes=True, spikemode='across')

  return dcc.Graph(figure=fig)
