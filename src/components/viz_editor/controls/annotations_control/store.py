def remove_annotation(data, index):
  """Remove an annotation by index, safely."""
  if not data or index is None or not (0 <= index < len(data)):
    return data
  data.pop(index)
  return data


def update_annotation(data, index, new_entry):
  """Insert or update an annotation at index."""
  if data is None:
    data = []
  if index is None:
    return data
  if index >= len(data):
    data.append(new_entry)
  else:
    data[index] = new_entry
  return data
