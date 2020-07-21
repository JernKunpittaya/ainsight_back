from model.core import ano_detection
import pmdarima as pm
import pandas as pd
from matplotlib import pyplot as plt


class ano_sarimax(ano_detection):
    def __init__(self, location, dateInput, y, splitby=None, stepFill=(1, 'days'), formatDate=None, groupby=None, d=None, D=None, periodicity=1):
        self.Data = self.set_axis(
            location=location, dateInput=dateInput, y=y, formatDate=formatDate)
        if splitby != None:
            self.Sp = self.split_by(
                Data=self.Data, Split=splitby, stepFill=stepFill, groupby=groupby)
        else:
            self.Sp = [[self.Data]]

        self.solution = list()
        self.graph_list = list()
        for i in self.Sp:
            self.solution.append(self.one_sarimax(
                Data=i[0], d=d, D=D, m=periodicity))
            if splitby != None:
                self.graph_list.append((dateInput, y, i[1]))
            else:
                self.graph_list.append((dateInput, y))

    def one_sarimax(self, Data, d, D, m):
        self.y = Data['value']
        self.index_of_fc = Data['date']
        self.model = pm.auto_arima(self.y, d=d, D=D, m=m)
        self.fitted = self.model.fit(self.y, disp=-1)

        self.Fit, self.confint = self.fitted.predict_in_sample(
            start=1, end=len(self.y), return_conf_int=True, alpha=0.05)
        self.X = pd.DataFrame()
        self.X['value'] = self.y
        self.X['date'] = self.index_of_fc
        self.X['lower_bound'] = (self.confint[:, 0])
        self.X['upper_bound'] = (self.confint[:, 1])
        self.X['isAnomaly'] = range(len(self.X))
        for i in range(len(self.X)):
            if (self.X['value'][i] > self.X['upper_bound'][i]) or (self.X['value'][i] < self.X['lower_bound'][i]):
                self.X['isAnomaly'][i] = True
            else:
                self.X['isAnomaly'][i] = False
        return self.X

    def print_anomaly(self):
        self.final_result = {}
        for i in range(len(self.solution)):
            if len(self.graph_list[0]) == 3:
                self.split = self.graph_list[i][2]
            else:
                self.split = "All"
            for j in range(len(self.solution[i])):
                self.solution[i]['date'].iloc[j] = self.solution[i]['date'].iloc[j].isoformat(
                )

            self.tuned_solution = (
                self.solution[i].set_index('date')).to_dict()
            self.data_list = list()
            for j in list(self.tuned_solution['value'].keys()):
                self.data_list.append({"dimension": {"date": j}, "value": round(self.tuned_solution['value'][j], 2), "isAnomaly": self.tuned_solution['isAnomaly'][j], "detail": {
                                      "lowerBound": round(self.tuned_solution['lower_bound'][j], 2), "upperBound": round(self.tuned_solution['upper_bound'][j], 2)}})
            self.result = {self.split: {"data_plot": self.data_list}}
            self.final_result.update(self.result)

        return self.final_result
