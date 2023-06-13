def simpleYield():
  i = 1
  while True:
    if i == 100:
      yield None
    yield i
    i += 1

for res in simpleYield():
  print(res)
  if res is None:
    break