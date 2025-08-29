from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

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
  path = BASE_DIR / 'data' / f'round{round_number}' / target / location / 'sample' / f'part-{part}.parquet'
  return path

def collect_data(path):
  path = Path(path)

  if not path.exists() or not path.is_file():
    print(f'Error: File not found at "{path}"')
    return None

  try:
    df = pd.read_parquet(path)
    return df.to_dict('records')
  except Exception as e:
    print(f'Error reading file "{path}": {e}')
    return None
