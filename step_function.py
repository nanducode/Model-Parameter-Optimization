

step = 1.6
param = 30
percent = 0.05

for i in range(10):
    param = param - (param * (percent * step))
    print(param)
