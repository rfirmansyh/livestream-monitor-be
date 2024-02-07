class CustomException(Exception):
  def __init__(self, details):
    self.details = details
    super().__init__()
    
def format_row_to_dict(row):
  d = {}
  for column in row.__table__.columns:
      d[column.name] = str(getattr(row, column.name))

  return d

