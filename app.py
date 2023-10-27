from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
#import logging
from datetime import timedelta, date

app = Flask(__name__)
CORS(app)

# Configura il logger per Loki con tracciamento
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger('loki_logger')

mysql_connection = mysql.connector.connect(
    host="mysql",
    user="admin",
    password="admin",
    port=3306,
    database="project"
)

@app.route("/stress_test")
def stress_test():
    def fibo(num):
        a, b = 1, 0
        while num >= 0:
            a, b = a + b, a
            num -= 1
        return b

    return str(fibo(1000))

@app.route("/post_name", methods=["POST"])
def post_name():
    data = request.get_json()
    name = data.get("name")
    print(name)
    return jsonify({"message": "Name received"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    employee_id = data.get("employee_id")
    password = data.get("password")
    app.logger.info(employee_id)
    app.logger.info(password)
    if employee_id and password:
        cursor = mysql_connection.cursor()
        cursor.execute("SELECT * FROM employee WHERE employee_id = %s AND password = %s", (employee_id, password))
        results = cursor.fetchall()
        cursor.close()

        if results:
            app.logger.info(jsonify({"token": results[0][0]}))
            return jsonify({"token": results[0][0]})
        else:
            return "Incorrect Username and/or Password", 401
    else:
        return "Please enter Username and Password", 400

@app.route("/book", methods=["POST"])
def book():
    data = request.get_json()
    employee_id = data.get("employee_id")
    room = data.get("room")
    date = data.get("date")
    time_s = data.get("time_s")
    time_e = data.get("time_e")

    if room and date and time_s and time_e:
        cursor = mysql_connection.cursor()
        cursor.execute("SELECT room_id FROM room WHERE name = %s", (room,))
        room_id = cursor.fetchone()[0]
        cursor.close()

        cursor = mysql_connection.cursor()
        cursor.execute("INSERT INTO reservations (employee_id, date, starting_time, ending_time, room_id) VALUES (%s, %s, %s, %s, %s)", (employee_id, date, time_s, time_e, room_id))
        cursor.close()

        cursor = mysql_connection.cursor()
        cursor.execute("SELECT * FROM reservations")
        results = cursor.fetchall()
        cursor.close()

        return jsonify({"token": "123"})
    else:
        return "Please enter all required fields", 400

# Funzione per convertire un oggetto timedelta in una rappresentazione serializzabile
def serialize_timedelta(td):
    return str(td)

# Funzione per convertire un oggetto datetime.date in una rappresentazione serializzabile
def serialize_date(dt):
    return dt.strftime('%Y-%m-%d')

@app.route("/myreservations", methods=["POST"])
def my_reservations():
    data = request.get_json()
    employee_id = data.get("employee_id")
    app.logger.info(employee_id)
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT * FROM reservations WHERE employee_id = %s", (employee_id,))
    results = cursor.fetchall()
    cursor.close()
    app.logger.info(results)
    # Serializza gli oggetti timedelta e datetime.date nella lista dei risultati
    serialized_results = []
    for row in results:
        reservation = {
            "id": row[0],
            "employee_id": row[1],
            "date": serialize_date(row[2]),
            "starting_time": serialize_timedelta(row[3]),
            "ending_time": serialize_timedelta(row[4]),
            "room_id": row[5]
        }
        serialized_results.append(reservation)
    app.logger.info(serialized_results)
    return jsonify(serialized_results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
