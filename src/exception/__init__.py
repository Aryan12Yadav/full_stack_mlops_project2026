import sys 
import logging
from typing import Union
from types import ModuleType

def error_message_detail(error: Union[Exception, str], error_detail: ModuleType) -> str:
    """ 
    Extract detailed error information including file name, line number , and the error message.
    :param error: The exception that occurred.
    : param error_tdetail: The sys module to access traceback details.
    :return : A formatted error message string."""
    
    #Extract traceback details ( exception information)
    _,_, exc_tb = error_detail.exc_info()

    # Get the file name where the excepton occurrred
    file_name = exc_tb.tb_frame.f_code.co_filename

    # Create a formatted error message string with file name, line number, and the acutal error
    line_number = exc_tb.tb_lineno
    error_message = f"Error occurred in python script: [{file_name}] at line number [{line_number}]:{str(error)}"

    #Log the error for better tracking
    logging.error(error_message)

    return error_message

class MyException(Exception):
    """ 
    Custom exception class for handling errors in teh US visa application
    """

    def __init__(self,error_message:str,error_detail:ModuleType):
        """
        Initializes the USvisaException with a detailed error message.
        :param error_message: A string descrbiing the eroor.
        :param error_detail: The sys modeule to access traceback details.
        """

        # Call the base class constructor with the error message
        super().__init__(error_message)

        # Format the dtailed error message using the error_message_detail function
        self.error_message = error_message_detail(error_message,error_detail)

    def __str__(self) -> str:
        """
        Return the string representation of the error message.
        """
        return self.error_message