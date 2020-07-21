import pandas as pd
import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt


class ano_detection():
    def __init__(self):
        print('This is just a parent class for anomaly detection')

    def split_by(self, Data, Split=None, stepFill=(1, 'days'), groupby=None):
        DataSplit = list()
        if(stepFill == None):
            # for i in Data[Split].unique():
            #     Sp = pd.DataFrame(Data[Data[Split] == i]).reset_index(drop=True)
            #     state = i
            #     for i in Sp.columns:
            #         if i != 'date' and i != 'value':
            #             Sp = Sp.drop(columns=[i])
            #     result = []
            #     start = Sp['date'][0]
            #     end = Sp['date'][len(Sp)-1]
            #     while start <= end:
            #         result.append(start)
            #         key = stepFill[1]
            #         start += relativedelta(**{key: stepFill[0]})
            #     idx = np.array(result)
            #     Sp.set_index('date', inplace=True)
            #     Sp = Sp.reindex(idx, fill_value=0)
            #     if groupby != None:
            #         Sp = Sp.resample(groupby).sum()
            #     Sp = Sp.reset_index()
            #     DataSplit.append((Sp, state))
            return Data

        else:
            for i in Data[Split].unique():
                Sp = pd.DataFrame(Data[Data[Split] == i]
                                  ).reset_index(drop=True)
                state = i
                for i in Sp.columns:
                    if i != 'date' and i != 'value':
                        Sp = Sp.drop(columns=[i])
                result = []
                start = Sp['date'][0]
                end = Sp['date'][len(Sp)-1]
                while start <= end:
                    result.append(start)
                    key = stepFill[1]
                    start += relativedelta(**{key: stepFill[0]})
                idx = np.array(result)
                Sp.set_index('date', inplace=True)
                Sp = Sp.reindex(idx, fill_value=0)
                if groupby != None:
                    Sp = Sp.resample(groupby).sum()
                Sp = Sp.reset_index()
                DataSplit.append((Sp, state))
            return DataSplit

    def set_axis(self, location, dateInput, y, formatDate=None):
        Data = location
        if (type(Data[dateInput][0]) != datetime.date) and (type(Data[dateInput][0]) != datetime.datetime) and (type(Data[dateInput][0]) != pd._libs.tslibs.timestamps.Timestamp):
            Data[dateInput] = (pd.to_datetime(
                Data[dateInput], format=formatDate))
        Data['date'] = Data[dateInput]
        Data['value'] = Data[y]
        return Data
