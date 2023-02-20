class Queries:

    CREATE_DETECTION_TABLE = """CREATE TABLE IF NOT EXISTS Detections (
	                    id INTEGER PRIMARY KEY,
	                    vehicle_type INTEGER NOT NULL,
	                    speed REAL NOT NULL,
   	                    created DATETIME NOT NULL,
	                    uploaded BOOLEAN NOT NULL DEFAULT 0
                    );"""

    CLEAR_DETECTION_TABLE = """DELETE FROM Detections where uploaded != 0"""

    INSERT_DETECTION_RECORD = """INSERT INTO Detections (vehicle_type, speed, created)
VALUES(@@type, @@speed, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))"""

    DETECTIONS_TO_UPLOAD = """SELECT json_object(
    'macaddress', "@@macaddress",
    'latitude', latitudevalue,
    'longitude', longitudevalue,
    'detections', json_group_array(
        json_object(
            'type', vehicle_type,
            'speed', speed,
            'time', created
        )
    )
) result
FROM Detections"""
