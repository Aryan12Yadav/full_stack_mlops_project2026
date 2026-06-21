#below code is to check the logging config
from src.logger import logging
from src.exception import MyException
logging.debug("This is a debug message")
import sys

try:
    a = 1+"2"

except Exception as e:
    logging.info(e)
    raise MyException(e,sys) from e

