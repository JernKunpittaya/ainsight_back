from flask import send_from_directory
import pandas as pd
from werkzeug.utils import secure_filename
from model.sesd import ano_sesd
from model.prophet import ano_prophet
from model.sarimax import ano_sarimax
from model.core import ano_detection
from flask import Flask, request, render_template, jsonify, make_response, flash, redirect, url_for
from flask_cors import CORS
import sys
import json
import os
from _collections import defaultdict
# sys.path.insert(1, 'C:/Users/USER/Desktop/Ainsight')
UPLOAD_FOLDER = "C:/Users/USER/Desktop/Ainsight/"
ALLOWED_EXTENSIONS = {'txt', 'xlsx', 'csv'}
ds_map = {}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"
CORS(app)


# @app.route("/")
# def greeting():
#     return "Welcome to Anomaly Detection"
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploadDS/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # print("DEBUGGED")
        # check if the post request has the file part
        # print(request.files)
        if 'files[0]' not in request.files:
            flash('No file part')
            # print("DEBUG 1")
        file = request.files['body']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            # print("DEBUG 2")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ds_map[filename] = os.path.join(
                app.config['UPLOAD_FOLDER'], filename)
            # print("FILE SAVED")
        update_ds()
        return ''''''

# # @cross_origin(origin='http://127.0.0.1',headers=['Content- Type','Authorization'])


@app.route('/datasets/', methods=['POST'])
def col_detail_api():
    update_ds()
    params = request.json
    if(params.get('ds', '') != '' and params.get('table', '') == ''):
        ds = params.get('ds')
        dff = pd.read_csv(ds_map[ds])
        df = dff.iloc[:, :]
        response = jsonify({'cols': dff.columns.to_list()})
    elif(params.get('table', '') != ''):
        ds = params.get('ds')
        dff = pd.read_csv(ds_map[ds])
        df = dff.iloc[:100, :]
        json_column = []
        for x in df.columns.to_list():
            temp = {}
            temp['key'] = x
            temp['dataKey'] = x
            temp['title'] = x
            temp['width'] = 150
            json_column.append(temp)
        df['id'] = df.index
        dd = df.to_json(orient='records')
        response = jsonify({'data': dd, 'columns': json_column})
    else:
        response = jsonify({'datasets': list(ds_map.keys())})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/sarimax", methods=['POST'])
def print_sarimax():
    location = request.get_json().get('location')
    location = pd.read_csv(ds_map[location])
    dateInput = request.get_json().get('dateInput')
    y = request.get_json().get('y')
    splitby = request.get_json().get('splitby')
    if splitby == "" or splitby == None:
        splitby = None
    stepFill = request.get_json().get('stepFill')
    if stepFill == "" or stepFill == None:
        stepFill = None
    else:
        stepFill = stepFill.split(" ")
        stepFill = (int(stepFill[0]), stepFill[1])
    formatDate = request.get_json().get('formatDate')
    groupby = request.get_json().get('groupby')
    if groupby == "" or groupby == None:
        groupby = None

    d = request.get_json().get('d')
    if d != "" and d != None:
        d = int(d)
    if d == "":
        d = None
    D = request.get_json().get('D')
    if D != "" and D != None:
        D = int(D)
    if D == "":
        D = None
    periodicity = request.get_json().get('period')
    if periodicity == "" or periodicity == None:
        periodicity = 1
    else:
        periodicity = int(periodicity)

    sarimax_object = ano_sarimax(location, dateInput, y, splitby, stepFill,
                                 formatDate, groupby,  d, D, periodicity)
    return sarimax_object.print_anomaly()


@app.route("/prophet", methods=['POST'])
def print_prophet():
    location = request.get_json().get('location')
    location = pd.read_csv(ds_map[location])
    dateInput = request.get_json().get('dateInput')

    y = request.get_json().get('y')
    splitby = request.get_json().get('splitby')
    if splitby == "" or splitby == None:
        splitby = None
    stepFill = request.get_json().get('stepFill')
    if stepFill == "" or stepFill == None:
        stepFill = None
    else:
        stepFill = stepFill.split(" ")
        stepFill = (int(stepFill[0]), stepFill[1])
    formatDate = request.get_json().get('formatDate')
    groupby = request.get_json().get('groupby')
    if groupby == "" or groupby == None:
        groupby = None
    interval_width = request.get_json().get('anomaly_ratio')
    if interval_width != "" and interval_width != None:
        interval_width = 1-float(interval_width)
    else:
        interval_width = 0.975
    changepoint_prior_scale = request.get_json().get('flexibility')
    if changepoint_prior_scale != "" and changepoint_prior_scale != None:
        changepoint_prior_scale = float(changepoint_prior_scale)
    else:
        changepoint_prior_scale = 0.5
    periodicity = request.get_json().get('period')
    if periodicity != "" and periodicity != None:
        periodicity = int(periodicity)
    if periodicity == "":
        periodicity = None
    prophet_object = ano_prophet(location, dateInput, y, splitby, stepFill, formatDate,
                                 groupby, interval_width, changepoint_prior_scale, periodicity)
    return prophet_object.print_anomaly()


@app.route("/sesd", methods=['POST'])
def print_sesd():
    location = request.get_json().get('location')
    location = pd.read_csv(ds_map[location])
    dateInput = request.get_json().get('dateInput')
    y = request.get_json().get('y')
    splitby = request.get_json().get('splitby')
    if splitby == "" or splitby == None:
        splitby = None
    stepFill = request.get_json().get('stepFill')
    if stepFill == "" or stepFill == None:
        stepFill = None
    else:
        stepFill = stepFill.split(" ")
        stepFill = (int(stepFill[0]), stepFill[1])
    formatDate = request.get_json().get('formatDate')
    groupby = request.get_json().get('groupby')
    if groupby == "" or groupby == None:
        groupby = None
    max_anomaly = request.get_json().get('max_anomaly')
    if max_anomaly != "" and max_anomaly != None:
        max_anomaly = int(max_anomaly)
    if max_anomaly == "":
        periodicity = None
    periodicity = request.get_json().get('period')
    if periodicity != "" and periodicity != None:
        periodicity = int(periodicity)
    if periodicity == "":
        periodicity = None

    sesd_object = ano_sesd(location, dateInput, y, splitby, stepFill,
                           formatDate, groupby, max_anomaly, periodicity)
    return sesd_object.print_anomaly()


def not_in_list(lis1, lis2):
    for x in lis1:
        if x not in lis2:
            return True
    return False


def custom_error(message, status_code):
    response = make_response(jsonify(message), status_code)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def update_ds():
    directory = UPLOAD_FOLDER
    for filename in os.listdir(directory):
        if filename.endswith(".csv") or filename.endswith(".xlsx"):
            ds_map[filename] = os.path.join(directory, filename)
            # print("ds_map ___ DEBUgGGGEDD ", ds_map)
        else:
            continue


update_ds()
if __name__ == "__main__":
    app.run(debug=True)
