def format_row_to_dict(row):
  d = {}
  for column in row.__table__.columns:
      d[column.name] = str(getattr(row, column.name))

  return d

def format_tuple_to_dict(tuple_data):
  return dict((y, x) for x, y in tuple_data)