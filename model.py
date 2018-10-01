

class Model:

    def __init__(self, name, res, parameters, step):
        self.name = name
        self.res = res # (NIGLOBAL, NJGLOBAL)
        self.parameters = parameters # list of model parameters
        self.step = step
        self.altered_params = {}
        self.run_name = name

    def alter_parameter(self, parameter, percent):
        """Decreases a parameter by a given percentage"""
        param = self.get_parameter(parameter)
        altered_parameter = param - (param * percent)
        self.altered_params[parameter] = altered_parameter

    def set_run_name(self, to_append):
        self.run_name = self.name + "_" + to_append.partition(".")[0]

    def get_parameter(self, param):
        if param in self.altered_params:
            return self.altered_params[param]
        else:
            return self.parameters[param]


def create_model_configurations():
    model_list = [] # list of models to return

    low = Model("1-2_deg",
                (44, 40),
                {"NIGLOBAL": 44,
                 "NJGLOBAL": 40,
                 "DT": 1200,
                 "KH": 13000},
                1.1)

    med = Model("1-4_deg",
                (88, 80),
                {"NIGLOBAL": 88,
                 "NJGLOBAL": 80,
                 "DT": 1200,
                 "KH": 150},
                 1.4)

    # high = Model("12km",
    #             (196, 180),
    #             {"NIGLOBAL": 196,
    #              "NJGLOBAL": 180,
    #              "DT": 600,
    #              "KH": 30},
    #              1.8)

    model_list = [low, med]
    return model_list
