from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import mysql.connector
import logging
from datetime import timedelta, date

app = Flask(__name__)

#cors = CORS(app, resources={r"/*": {"origins": "*"}})
#CORS(app)
#CORS(app, resources={r"/*": {"origins": "http://desk-reservation-app.example.com"}})

#app.config['CORS_HEADERS'] = 'Content-Type'
def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response
def build_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

standard_log = logging.getLogger("werkzeug")
#standard_log.disabled = True

# Configura il logger per Loki con tracciamento
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('loki_logger')

# Imposta il formato del logger per includere traceid e spanid
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.uuid = None
        if flask.has_request_context():
            record.uuid = g.uuid if hasattr(g, 'uuid') else None
            record.path = request.path
            record.endpoint = request.endpoint
            record.remote_addr = request.remote_addr
        return super(CustomFormatter, self).format(record)

custom_format = '''"traceid":"%(traceId)s", "spanid":"%(spanId)"s %(levelname)s %(name)s %(uuid)s %(path)s %(endpoint)s %(remote_addr)s  %(message)s'''
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter(fmt=custom_format))
logger.addHandler(handler)

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

@app.route("/book", methods=["POST"])
@cross_origin()
def book():
    try:
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

            app.logger.info("Reservation correctly registered")
            return jsonify({"token": "123"})
        else:
            app.logger.error("Error in parsing required fields...")
            return "Please enter all required fields", 400
    except Exception as e:
        app.logger.error(f'Error while registering the reservation": {str(e)}')
        return "An error occurred.", 500

# Funzione per convertire un oggetto timedelta in una rappresentazione serializzabile
def serialize_timedelta(td):
    return str(td)

# Funzione per convertire un oggetto datetime.date in una rappresentazione serializzabile
def serialize_date(dt):
    return dt.strftime('%Y-%m-%d')

@app.route("/myreservations", methods=["OPTIONS","POST"])
def my_reservations():
    try:
        if request.method == 'OPTIONS': 
            return build_preflight_response()
        elif request.method == 'POST': 
            data = request.get_json()
            employee_id = data.get("employee_id")
            app.logger.info("employee_id: " + employee_id)
            cursor = mysql_connection.cursor()
            cursor.execute("SELECT * FROM reservations WHERE employee_id = %s", (employee_id,))
            results = cursor.fetchall()
            cursor.close()
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
            return build_actual_response(jsonify(serialized_results))
    except Exception as e:
        app.logger.error(f'Error in recovering the reservations": {str(e)}')
        return "An error occurred.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", use_reloader=False, port=5000, debug=True)
