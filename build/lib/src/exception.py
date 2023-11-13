import sys
from src.logger import logging

def error_message_details(error,error_detail:sys):
    _,_,exc_tb = error_detail.exc_info()
    # print(error_detail.exc_info())
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = f"Error: {error} \n File Name: {file_name} \n Line Number: {exc_tb.tb_lineno}"

    return error_message

class CustomException(Exception):

    def __init__(self, error_message, error_detail:sys):
        super().__init__(error_message)
        self.error_message = error_message_details(error_message,error_detail=error_detail)
        logging.error(self.error_message)

    def __str__(self):
        return self.error_message
    
if __name__ == "__main__":
    logging.info("Logging has started")
    try:
        a = 1/0
    except Exception as e:
        logging.info('Division by zero')
        raise CustomException(e,sys)
    print('REACHED BEYOND')