from model.core import ano_detection
from fbprophet import Prophet
from matplotlib import pyplot as plt
import pandas as pd
import json


class ano_prophet(ano_detection):
    def __init__(self, location, dateInput, y, splitby=None, stepFill=(1, 'days'), formatDate=None, groupby=None, interval_width=0.975, changepoint_prior_scale=0.5, periodicity=None):
        self.Data = self.set_axis(location=location, dateInput=dateInput, y=y,
                                  formatDate=formatDate)
        if splitby != None:
            self.Sp = self.split_by(
                Data=self.Data, Split=splitby, stepFill=stepFill, groupby=groupby)
        else:
            self.Sp = [[self.Data]]

        self.solution = list()
        self.graph_list = list()
        for i in self.Sp:
            self.solution.append(self.one_prophet(
                Data=i[0], interval_width=interval_width, changepoint_prior_scale=changepoint_prior_scale, season=periodicity))
            if splitby != None:
                self.graph_list.append((dateInput, y, i[1]))
            else:
                self.graph_list.append((dateInput, y))

    def fit_predict_model(self, dataframe, interval_width, changepoint_prior_scale, season):
        self.m = Prophet(daily_seasonality=False, yearly_seasonality=False, weekly_seasonality=False,
                         seasonality_mode='additive',
                         interval_width=interval_width,
                         changepoint_prior_scale=changepoint_prior_scale)
        if season != None:
            self.m.add_seasonality(name='Custom season',
                                   period=season, fourier_order=5)
        self.m = self.m.fit(dataframe)
        self.forecast = self.m.predict(dataframe)
        self.forecast['fact'] = dataframe['y'].reset_index(drop=True)
        return self.forecast

    def one_prophet(self, Data, interval_width, changepoint_prior_scale, season):
        self.PData = pd.DataFrame()
        self.PData['y'] = Data['value']
        self.PData['ds'] = Data['date']
        self.X = self.fit_predict_model(dataframe=self.PData, interval_width=interval_width,
                                        changepoint_prior_scale=changepoint_prior_scale, season=season)
        self.X['isAnomaly'] = range(len(self.X))

        for i in range(len(self.X)):
            if (self.X['fact'][i] > self.X['yhat_upper'][i]) or (self.X['fact'][i] < self.X['yhat_lower'][i]):
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
                self.solution[i]['ds'].iloc[j] = self.solution[i]['ds'].iloc[j].isoformat(
                )

            self.tuned_solution = (self.solution[i].set_index('ds')).to_dict()
            self.data_list = list()
            for j in list(self.tuned_solution['fact'].keys()):
                self.data_list.append({"dimension": {"date": j}, "value": round(self.tuned_solution['fact'][j], 2), "isAnomaly": self.tuned_solution['isAnomaly'][j], "detail": {
                                      "lowerBound": round(self.tuned_solution['yhat_lower'][j], 2), "upperBound": round(self.tuned_solution['yhat_upper'][j], 2)}})
            self.result = {self.split: {"data_plot": self.data_list}}
            self.final_result.update(self.result)

        return self.final_result
