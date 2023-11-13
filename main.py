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

    file_name = "reviews_"+datetime.now().strftime('%m_%d_%Y_%H_')+process_number.__str__()+".csv"
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
        csv_file = open(file_path, 'w')
        if csv_file != None:
            writer = csv.writer(csv_file)
            for index,row in df.iterrows():
                if index%PROCESS_NUM == process_number:
                    new_reviews = scrapper.get_maps_data(row[0])
                    for review in new_reviews:
                        writer.writerow([row[0],row[1],review[0],review[1]])
            csv_file.close()
    except Exception as e:
        logging.info("Exception in scrape function in main.py")
        raise CustomException(e,sys)

    scrapper.close_scrapper()

if __name__ =="__main__":
    process_count = PROCESS_NUM
    processes = list()
    for process_num in range(process_count):
        processes.append(multiprocessing.Process(target=scrape, args=(process_num,)))


    for prcs in processes:
        prcs.start()

    for prcs in processes:
        prcs.join()
    print("done")

    
