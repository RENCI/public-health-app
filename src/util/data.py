from pathlib import Path

import pandas as pd

from components.chart import Location
from components.enums import DataType, Target

BASE_DIR = Path(__file__).resolve().parent.parent


def build_dataset_path(
  *,
  data_type: DataType = DataType.SAMPLE,
  round_number: int = 1,
  location: Location = Location('US'),
  target: Target = Target.INCIDENT_HOSPITALIZATION,
  part: int = 0,
) -> Path:
  part = str(part)
  round_fragment = f'round{round_number}'
  path = (
    BASE_DIR
    / round_fragment
    / str(target)
    / location.name
    / data_type.get_path_value()
    / f'part-{part}.{data_type.get_file_extension()}'
  )
  print(path)
  if not path.exists() or not path.is_file():
    raise FileNotFoundError(f'File not found for chart: {path}')
  return path


def collect_data(data_type: DataType, path: Path) -> pd.DataFrame:
  if not path.exists() or not path.is_file():
    raise FileNotFoundError(f'File not found for chart: {path}')

  try:
    if data_type == DataType.QUARTILE and path.suffix == '.csv':
      df = pd.read_csv(path, engine='pyarrow')
    elif data_type == DataType.SAMPLE and path.suffix == '.parquet':
      df = pd.read_parquet(path, engine='pyarrow')
    else:
      raise ValueError(f'Path file extension does not match data type: {path}, {data_type}')
    return df
  except Exception as e:
    print(f'Error reading file "{path}": {e}')
    raise e
