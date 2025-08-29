from pathlib import Path

def build_dataset_path(
  *,
  pathogen: str = 'flu',
  round_number: int = 1,
  location: str = 'US',
  target: str = 'incident_hospitalization',
  part: int = 0,
) -> Path:
  pathogen = str(pathogen or 'flu')
  round_number = str(round_number or 1)
  location = str(location or 'US')
  target = str(target or 'incident_hospitalization')
  part = str(part or 0)
  path = Path('data') / 'visualization' / 'data-visualization' / pathogen / f'round{round_number}' / target / location / 'sample' / f'part-{part}.parquet'
  return path
