import json
import sqlite3

from queries import Queries

DATABASE_NAME = "camerAi.db"


class DatabaseHelper:
    def __init__(self):
        self.con = sqlite3.connect(DATABASE_NAME)

    def create_table(self):
        self.__execute_close_commit(Queries.CREATE_DETECTION_TABLE)

    def clear_table(self):
        self.__execute_close_commit(Queries.CLEAR_DETECTION_TABLE)

    def to_upload(self, mac_address, latitude, longitude):
        cur = self.con.cursor()
        res = cur.execute(Queries.DETECTIONS_TO_UPLOAD.replace('@@macaddress', str(mac_address)).replace('latitudevalue', latitude).replace('longitudevalue', longitude))
        return res.fetchone()[0]

    def insert_detection(self, vehicle_type, speed):
        qry = Queries.INSERT_DETECTION_RECORD \
            .replace('@@type', str(vehicle_type)) \
            .replace('@@speed', str(speed))
        self.__execute_close_commit(qry)

    def __execute_close_commit(self, qry):
        cur = self.con.cursor()
        cur.execute(qry)
        self.con.commit()
        cur.close()
