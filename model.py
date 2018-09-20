

class Model:

    def __init__(self, name, res, configs):
        self.name = name
        self.res = res # (NIGLOBAL, NJGLOBAL)
        self.configs = configs # list of model configurations



def create_model_configurations():
    model_list = [] # list of models to return

    low = Model("low",
                (44, 40),
                {"NIGLOBAL": "44",
                 "NJGLOBAL": "40",
                 "DT": "1200",
                 "KH": "1.0E+04"})

    med = Model("med",
                (88, 80),
                {"NIGLOBAL": "88",
                 "NJGLOBAL": "80",
                 "DT": "600",
                 "KH": "1.0E+02"})

    high = Model("high",
                (196, 180),
                {"NIGLOBAL": "196",
                 "NJGLOBAL": "180",
                 "DT": "300",
                 "KH": "1.0E+01"})

    model_list = [low, med, high]
    return model_list
