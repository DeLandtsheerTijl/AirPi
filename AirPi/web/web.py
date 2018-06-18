import logging
import os
import json
from flask import Flask, g, request, abort, flash, render_template, redirect, url_for
from flaskext.mysql import MySQL
from flask_httpauth import HTTPBasicAuth
from functools import wraps

from flask import make_response
from passlib import pwd
from passlib.hash import argon2

log = logging.getLogger(__name__)
app = Flask(__name__, template_folder='./templates')
mysql = MySQL(app)
auth = HTTPBasicAuth()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'airpi-web'
app.config['MYSQL_DATABASE_PASSWORD'] = '!CBy7rXGmB9.'
app.config['MYSQL_DATABASE_DB'] = 'dbairpi'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# session config
app.secret_key = pwd.genword(entropy=128)

def get_data(sql, params=None):
    conn = mysql.connect()
    cursor = conn.cursor()
    print("getting data")
    try:
        print(sql)
        cursor.execute(sql, params)
    except Exception as e:
        print(e)
        return False

    result = cursor.fetchall()
    data = []
    for row in result:
        data.append(list(row))
    cursor.close()
    conn.close()

    return data


def set_data(sql, params=None):
    conn = mysql.connect()
    cursor = conn.cursor()
    print("Setting Data")
    try:
        print(sql)
        cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        print(e)
        return False

    # result = cursor.fetchall()
    # data = []
    # for row in result:
    # data.append(list(row))
    data = "Done"
    cursor.close()
    conn.close()
    print("Done")

    return data

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    data = []
    temp = get_data("SELECT round(D.sensordata, 1) FROM tbldata AS D JOIN tblsensor AS S on S.idsensor = D.sensorid WHERE S.sensorname LIKE 'Temperature' ORDER BY D.iddata DESC LIMIT 1")[0][0]
    hum = get_data("SELECT round(D.sensordata) FROM tbldata AS D JOIN tblsensor AS S on S.idsensor = D.sensorid WHERE S.sensorname LIKE 'Humidity' ORDER BY D.iddata DESC LIMIT 1")[0][0]
    co2 = get_data("SELECT round(D.sensordata) FROM tbldata AS D JOIN tblsensor AS S on S.idsensor = D.sensorid WHERE S.sensorname LIKE 'co2' ORDER BY D.iddata DESC LIMIT 1")[0][0]
    tvoc = get_data("SELECT round(D.sensordata) FROM tbldata AS D JOIN tblsensor AS S on S.idsensor = D.sensorid WHERE S.sensorname LIKE 'tvoc' ORDER BY D.iddata DESC LIMIT 1")[0][0]
    print("----------------------------------{0}".format(request.cookies.get("session")))
    return render_template("index.html", temp=temp, hum=hum, co2=co2, tvoc=tvoc, status = "Logout")

@app.route('/temperature')
@login_required
def temperature():
    temp = get_data("SELECT round(D.sensordata, 1) FROM tbldata AS D JOIN tblsensor AS S on S.idsensor = D.sensorid WHERE S.sensorname LIKE 'Temperature' ORDER BY D.iddata DESC LIMIT 1")[0][0]
    timeofmeasurement = get_data("SELECT DATE_FORMAT(timeofmeasurement,'%H:%i') FROM tbldata WHERE sensorid = 1 ORDER BY iddata DESC LIMIT 30")
    sensordata = get_data("SELECT CAST(sensordata AS CHAR) FROM tbldata WHERE sensorid = 1 ORDER BY iddata DESC LIMIT 30")

    data_day = get_data("SELECT round(min(sensordata), 1), round(avg(sensordata), 1), round(max(sensordata), 1) FROM tbldata WHERE sensorid = 1 AND timeofmeasurement >= now() - INTERVAL 1 DAY;")
    data_week = get_data("SELECT round(min(sensordata), 1), round(avg(sensordata), 1), round(max(sensordata), 1) FROM tbldata WHERE sensorid = 1 AND timeofmeasurement >= now() - INTERVAL 1 WEEK;")

    #tom = removelistitem(timeofmeasurement)
    #tom = ["test", "test"]
    print(timeofmeasurement)
    return render_template("temperature.html", data_day = data_day, data_week = data_week, temp = temp, tom = timeofmeasurement[::-1], sensordata = sensordata[::-1], status = "Logout")

@app.route('/humidity')
@login_required
def humidity():
    hum = get_data("SELECT round(D.sensordata) FROM tbldata AS D JOIN tblsensor AS S on S.idsensor = D.sensorid WHERE S.sensorname LIKE 'Humidity' ORDER BY D.iddata DESC LIMIT 1")[0][0]
    timeofmeasurement = get_data("SELECT DATE_FORMAT(timeofmeasurement,'%H:%i') FROM tbldata WHERE sensorid = 2 ORDER BY iddata DESC LIMIT 30")
    sensordata = get_data("SELECT CAST(sensordata AS CHAR) FROM tbldata WHERE sensorid = 2 ORDER BY iddata DESC LIMIT 30")

    data_day = get_data("SELECT round(min(sensordata)), round(avg(sensordata)), round(max(sensordata)) FROM tbldata WHERE sensorid = 2 AND timeofmeasurement >= now() - INTERVAL 1 DAY;")
    data_week = get_data("SELECT round(min(sensordata)), round(avg(sensordata)), round(max(sensordata)) FROM tbldata WHERE sensorid = 2 AND timeofmeasurement >= now() - INTERVAL 1 WEEK;")

    return render_template("humidity.html", data_day = data_day, data_week = data_week, hum = hum, tom = timeofmeasurement[::-1], sensordata = sensordata[::-1], status = "Logout")

@app.route('/airquality')
@login_required
def airquality():
    co2 = get_data("SELECT round(D.sensordata) FROM tbldata AS D JOIN tblsensor AS S on S.idsensor = D.sensorid WHERE S.sensorname LIKE 'co2' ORDER BY D.iddata DESC LIMIT 1")[0][0]
    tvoc = get_data("SELECT round(D.sensordata) FROM tbldata AS D JOIN tblsensor AS S on S.idsensor = D.sensorid WHERE S.sensorname LIKE 'tvoc' ORDER BY D.iddata DESC LIMIT 1")[0][0]
    timeofmeasurement = get_data("SELECT DATE_FORMAT(timeofmeasurement,'%H:%i') FROM tbldata WHERE sensorid = 3 ORDER BY iddata DESC LIMIT 30")
    sensordata = get_data("SELECT CAST(sensordata AS CHAR) FROM tbldata WHERE sensorid = 3 ORDER BY iddata DESC LIMIT 30")

    return render_template("airquality.html", co2 = co2, tvoc = tvoc, tom = timeofmeasurement[::-1], sensordata = sensordata[::-1], status = "Logout")


def removelistitem(list):
    result = []
    list.reverse()
    for i in list:
        result.append(i[0])
    print(result)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    g.user = None

    result = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email and password:
            abort(400)
        authorized = verify_credentials(email, password)
        if authorized == True:
            print("-----------{0}".format(g.user))
            flash(g.user)
            response = make_response(redirect("/"))
            return response
        else:
            flash("The adres or password you entered is incorrect.", "error")
            return render_template("login.html")
    else:
        return render_template("login.html")

def add_user(idemail, username, password):
    try:
        if get_data('SELECT phcstring FROM dbairpi.tbluser WHERE idemail=%s', idemail):
            message = 'There is already an account using {}.'.format(idemail)
            log.info(message)
            category = "error"
            return False, message, category

        argon_hash = argon2.hash(password)
        if set_data('INSERT INTO dbairpi.tbluser (idemail, username, phcstring) VALUES (%s, %s, %s);', (idemail, username, argon_hash)):
            message = 'Added user {}'.format(idemail)
            log.info(message)
            category = "success"
            return True, message, category

    except Exception as e:
        print("ERROR")
        category = "error"
        message = 'Error adding user {}: {}'.format(idemail, e)
        log.error(message)
        return False, message, category

@auth.verify_password
def verify_credentials(idemail, password):
    record = get_data('SELECT phcstring FROM dbairpi.tbluser WHERE idemail=%s', (idemail,))
    print(record)
    if not record:
        return False
    authorized = argon2.verify(password, record[0][0])
    if authorized:
        g.user = idemail
    return authorized


#@app.route('/secure')
#@auth.login_required
#def secure():
#    return 'Hello, {}!'.format(g.user)

@app.before_request
def before_request():
    g.user = request.cookies.get("session")

@app.route('/register', methods=['GET', 'POST'])
def register():
    result = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        if not email and password and username:
            abort(400)
        result, message, category = add_user(email.lower(), username, password)
        flash(message, category)
        return redirect(url_for('login', next=request.url))
    return render_template('register.html', success=result)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log.info("Flask app starting")
    app.run(host='0.0.0.0', debug=True, threaded=True)
    #port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
