import os, csv
import pandas as pd
from src.scrapper import Scrapper
from src.logger import logging
from src.exception import CustomException
from datetime import datetime

# import threading
import multiprocessing
import time
import sys

PROCESS_NUM = 5
TIMEOUT = 10

if (len(sys.argv))>1:
    PROCESS_NUM = int(sys.argv[1])
if (len(sys.argv))>2:
    TIMEOUT = int(sys.argv[2])

if multiprocessing.current_process().name == "MainProcess":
    logging.info(f"{PROCESS_NUM} Scraping Processes running in parallel")
    logging.info(f"TIMEOUT set to -> {TIMEOUT} secs")

def scrape(process_number: int):
    scrapper = Scrapper()
    scrapper.set_url("https://www.google.com/maps/")
    scrapper.set_timeout(TIMEOUT)
    data = []
    data_path = os.path.join("data","Assignment.xlsx")
    excel_keywords = pd.read_excel(data_path)
    df = pd.DataFrame(excel_keywords)

    file_name = "reviews_"+datetime.now().strftime('%m_%d_%Y_%H_%M')+process_number.__str__()+".csv"
    file_dir_name = datetime.now().strftime('%m_%d_%Y_%H')
    dir_path = os.path.join(os.getcwd(),"extracted_data",file_dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path,file_name)

    try:
        file_exists = os.path.isfile(file_path)
        if not file_exists:
            csv_file = open(file_path, 'w')
            if csv_file != None:
                writer = csv.writer(csv_file)
                writer.writerow(['Property','Address','reviewer_name','review'])
                csv_file.close()
        # scrapper.busy_wait_till_page_load(4)
        # csv_file = open(file_path, 'w')
        # if csv_file != None:
            # writer = csv.writer(csv_file)
        for index,row in df.iterrows():
            if index%PROCESS_NUM == process_number:
                new_reviews = scrapper.get_maps_data(row[0])
                with open(file_path, 'a') as csv_file:
                    writer = csv.writer(csv_file)
                    for review in new_reviews:
                        writer.writerow([row[0],row[1],review[0],review[1]])
            # csv_file.close()
    except Exception as e:
        logging.info("Exception in scrape function in main.py")
        raise CustomException(e,sys)

    scrapper.close_scrapper()

# class CallingClass(Scrapper):
#     def __init__(self, url: str = None) -> None:
#         super().__init__(url)

#     def test_function(self):
#         # scrapper = Scrapper()
#         site_url = "https://www.google.com/maps/search/Central+park+I/@28.5270195,76.935776,11z/data=!3m1!4b1?entry=ttu"
#         self.set_url(site_url)
#         self.set_timeout(TIMEOUT)
#         self.driver.get(self.url)
#         self.driver.maximize_window()
#         self.busy_wait_till_page_load(4)

#         print(self._Scrapper__collect_property_list_from_scroll_div_and_get_reviews())
        
#         self.close_scrapper()


if __name__ =="__main__":
    # testClass = CallingClass()
    # testClass.test_function()


    # # # scrape(100)

    process_count = PROCESS_NUM
    processes = list()
    for process_num in range(process_count):
        processes.append(multiprocessing.Process(target=scrape, args=(process_num,)))


    for prcs in processes:
        prcs.start()

    for prcs in processes:
        prcs.join()
        
    print("done")

    
