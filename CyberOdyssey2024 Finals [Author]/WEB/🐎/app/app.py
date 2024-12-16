from flask import Flask, request, jsonify
import mysql.connector
import time
import threading
import os

FLAG = os.environ["FLAG"]

app = Flask(__name__)

db_config_worker = {
    'host': 'db',
    'user': 'worker',
    'password': 'password',
    'database': 'db'
}

db_config_user = {
    'host': 'db',
    'user': 'user',
    'password': 'password',
    'database': 'db'
}

def get_db_connection_worker():
    return mysql.connector.connect(**db_config_worker)

def get_db_connection_user():
    return mysql.connector.connect(**db_config_user)

def mysql_wakeup():
    while True:
        try:
            connection = mysql.connector.connect(**db_config_worker)
            connection.close()
            print("MySQL is ready")
            break
        except mysql.connector.Error as err:
            print(f"MySQL not ready yet: {err}")
            time.sleep(5)

def worker():
    while True:
        connection = get_db_connection_worker()
        cursor = connection.cursor()
        try:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            cursor.execute("START TRANSACTION")
            cursor.execute("SELECT * FROM FLAG FOR UPDATE")
            cursor.fetchall()
            cursor.execute(f"ALTER TABLE FLAG ADD COLUMN `{FLAG}` VARCHAR(255)")
            cursor.execute(f"UPDATE FLAG SET `{FLAG}` = '{FLAG}'")
            cursor.execute(f"ALTER TABLE FLAG DROP COLUMN `{FLAG}`")
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"Transaction failed: {e}\n", file=__import__('sys').stderr)
        finally:
            cursor.close()
            connection.close()
        time.sleep(120)

@app.route('/🐎', methods=['POST'])
def sql():
    try:
        query = request.json.get('sql')
        if not query:
            return jsonify({"error": "SQL query is required"}), 400
        if not isinstance(query, str):
            return jsonify({"?": "?"})
    
        connection = get_db_connection_user()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
            return jsonify(result)

        connection.commit()
        return jsonify({"?": "?"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    mysql_wakeup()
    threading.Thread(target=worker, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
