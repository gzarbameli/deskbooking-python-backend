from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import mysql.connector
import logging
from datetime import timedelta, date
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

CORS(app)

FlaskInstrumentor().instrument_app(app)

standard_log = logging.getLogger("werkzeug")
standard_log.disabled = True

# Configura il logger per Loki con tracciamento
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('loki_logger')

class CustomFormatter(logging.Formatter):
    def format(self, record):
        if flask.has_request_context():
            # Estrai l'ID del trace e dello span dal contesto di tracciamento
            current_span = trace.get_current_span()
            trace_id = current_span.get_span_context().trace_id
            span_id = current_span.get_span_context().span_id
        else:
            trace_id = None
            span_id = None
        
        record.traceId = trace_id
        record.spanId = span_id
        
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

@app.route("/book", methods=["OPTIONS","POST"])
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
        return jsonify(serialized_results)
    except Exception as e:
        app.logger.error(f'Error in recovering the reservations": {str(e)}')
        return "An error occurred.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", use_reloader=False, port=5000, debug=True)
