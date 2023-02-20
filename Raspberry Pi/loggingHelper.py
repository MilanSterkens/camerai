import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


class LoggingHelper(object):

    @staticmethod
    def configure():
        path = "logs"
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)

        logger = logging.getLogger('main')
        fh = logging.FileHandler('{:%Y-%m-%d}.log'.format(datetime.now()))
        handler = TimedRotatingFileHandler(filename="logs/" + datetime.now().strftime('%Y_%m_%d.log'), when='D', interval=1, backupCount=90,
                                           encoding='utf-8', delay=False)
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.addHandler(fh)
        return logger
