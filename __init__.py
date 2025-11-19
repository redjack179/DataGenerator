    import logging
    import random
    import datetime
    import json
    import os
    import pyodbc
    import azure.functions as func

    def main(req: func.HttpRequest) -> func.HttpResponse:
        logging.info('Python HTTP trigger function processed a request.')

        try:
            req_body = req.get_json()
            sensor_count = int(req_body.get('sensorCount', 10))
        except (ValueError, AttributeError):
            sensor_count = 10

        conn_str = os.environ["SqlConnectionString"]
        
        data_to_insert = []
        for i in range(sensor_count):
            sensor_id = f"Sensor_{i+1}"
            temperature = round(random.uniform(15.0, 30.0), 2)
            co2_level = round(random.uniform(400.0, 1000.0), 2)
            timestamp = datetime.datetime.utcnow()
            data_to_insert.append((sensor_id, temperature, co2_level, timestamp))

        try:
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                sql_insert_query = """
                    INSERT INTO dbo.SensorData (SensorID, Temperature, CO2Level, Timestamp)
                    VALUES (?, ?, ?, ?);
                """
                cursor.executemany(sql_insert_query, data_to_insert)
                conn.commit()
                logging.info(f"Successfully inserted {cursor.rowcount} rows.")
                
                return func.HttpResponse(
                    f"Successfully inserted {cursor.rowcount} rows into the database.",
                    status_code=200
                )

        except Exception as e:
            logging.error(f"Error connecting to database or inserting data: {e}")
            return func.HttpResponse(
                "Error connecting to the database or inserting data.",
                status_code=500
            )
