from flask import Flask
import threading
import time
import csv
import psycopg2
import os

app = Flask(__name__)

# Environment config
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CSV_FILE = 'animals.csv'

# Control variables
inserting = False
inserter_thread = None
insert_index = 0

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def insert_next_row():
    global insert_index
    try:
        with open(CSV_FILE, newline='') as csvfile:
            reader = list(csv.DictReader(csvfile))
            print(f"[DEBUG] Total rows in CSV: {len(reader)}")

            if insert_index >= len(reader):
                print("All records inserted.")
                return

            row = reader[insert_index]
            print(f"[DEBUG] Attempting to insert row {insert_index + 1}: {row}")

            conn = get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS animals (
                    name TEXT,
                    species TEXT,
                    height_cm INTEGER,
                    weight_kg INTEGER
                );
            ''')
            cur.execute("INSERT INTO animals (name, species, height_cm, weight_kg) VALUES (%s, %s, %s, %s)",
                        (row['name'], row['species'], int(row['height_cm']), int(row['weight_kg'])))
            conn.commit()
            cur.close()
            conn.close()
            print(f"[INFO] Inserted record {insert_index + 1}: {row}")
            insert_index += 1

    except FileNotFoundError:
        print(f"[ERROR] CSV file '{CSV_FILE}' not found!")
    except Exception as e:
        print(f"[ERROR] insert_next_row exception: {e}")

def inserter_job():
    global inserting
    print("[DEBUG] Inserter job started.")
    while inserting:
        insert_next_row()
        time.sleep(120)

@app.route('/')
def hello_world():
    return "Flask Zoo App is running."

@app.route('/start-inserting')
def start_inserting():
    global inserting, inserter_thread
    if not inserting:
        inserting = True
        inserter_thread = threading.Thread(target=inserter_job, daemon=True)
        inserter_thread.start()
        return "Started inserting animal records every 2 minutes."
    return "Already inserting."

@app.route('/stop-inserting')
def stop_inserting():
    global inserting
    inserting = False
    return "Stopped inserting animal records."

if __name__ == '__main__':
    print("[INFO] Starting app...")
    insert_next_row()  # Immediate insert for testing
    app.run(host='0.0.0.0', port=5000)
