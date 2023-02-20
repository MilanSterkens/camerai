import databaseHelper
import schedule
import time
import uuid

from loggingHelper import LoggingHelper
from atModem import AtModem
from aiDetection import AiDetection
from dotenv import load_dotenv

UPLOAD_TIME = "04:00"
RETRY_INTERVAL = 1

logger = LoggingHelper.configure()
load_dotenv()

dbHelper = databaseHelper.DatabaseHelper()

dbHelper.create_table()


def upload_detections():
    try:
        schedule.clear()
        atModem = AtModem()
        coords = atModem.get_gps()
        res = dbHelper.to_upload(uuid.getnode(), coords[0], coords[1])
        response = atModem.upload_data(res)
        atModem.close()
        atModem.uninstall_device()
        del res
        del atModem
        if response:
            logger.info('successfully upload records')
            dbHelper.clear_table()
            schedule.every().day.at(UPLOAD_TIME).do(upload_detections)
            logger.info('successfully cleared database')
            return
        schedule.every(RETRY_INTERVAL).minutes.do(upload_detections)
    except Exception as e:
        schedule.every(RETRY_INTERVAL).minutes.do(upload_detections)
        logger.critical('Failed to upload with exception', e)


schedule.every().day.at(UPLOAD_TIME).do(upload_detections)
AiDetection(dbHelper)
