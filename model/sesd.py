
from model.core import ano_detection
import sesd
import pandas as pd
from matplotlib import pyplot as plt


class ano_sesd(ano_detection):
    def __init__(self, location, dateInput, y, splitby=None, stepFill=(1, 'days'), formatDate=None, groupby=None, max_anomaly=None, periodicity=None):
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
            self.solution.append(self.one_sesd(
                Data=i[0], max_anomaly=max_anomaly, periodicity=periodicity))
            if splitby != None:
                self.graph_list.append((dateInput, y, i[1]))
            else:
                self.graph_list.append((dateInput, y))

    def one_sesd(self, Data, max_anomaly=None, periodicity=None):
        self.X = Data
        if max_anomaly == None:
            max_anomaly = int(0.1*len(self.X))
        self.outliers_indices = sesd.seasonal_esd(self.X['value'], hybrid=True,
                                                  max_anomalies=max_anomaly, periodicity=periodicity)
        self.sesd_anomaly_column = 'isAnomaly'
        self.X[self.sesd_anomaly_column] = False
        self.X.loc[self.X.index.isin(
            self.outliers_indices), self.sesd_anomaly_column] = True
        # self.anomaly=self.X[self.X['value_SESD_Anomaly']==True]
        # self.anomaly[['date','value']]
        return (self.X)

    def print_anomaly(self):
        self.final_result = {}
        for i in range(len(self.solution)):
            if len(self.graph_list[0]) == 3:
                #split="split "+str(i+1)+" "+self.graph_list[i][2]
                self.split = self.graph_list[i][2]
            else:
                #split="split "+str(i+1)
                self.split = "All"

            for j in range(len(self.solution[i])):
                self.solution[i]['date'].iloc[j] = self.solution[i]['date'].iloc[j].isoformat(
                )

            self.tuned_solution = (
                self.solution[i].set_index('date')).to_dict()
            self.data_list = list()
            for j in list(self.tuned_solution['value'].keys()):
                self.data_list.append({"dimension": {
                                      "date": j}, "value": round(self.tuned_solution['value'][j], 2), "isAnomaly": self.tuned_solution['isAnomaly'][j], "detail": {}})
            self.result = {self.split: {"data_plot": self.data_list}}
            self.final_result.update(self.result)

        return self.final_result
