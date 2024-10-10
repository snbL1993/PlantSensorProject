import psycopg2
#raspberry_data
#sensor_data

conn =psycopg2.connect(
    host="192.168.178.60",
    port= 5432,database="test_sensor",
    user="postgres",
    password="database"
    )
conn.autocommit = True

cur = conn.cursor()
query_sensor_data = 'INSERT INTO {} VALUES(uuid_generate_v4(),now(),{},{},{},{},{},{});'

cur.execute(query_sensor_data.format("sensor_data",11,22,33,44,55,"mac"))

cur.close()
conn.close()