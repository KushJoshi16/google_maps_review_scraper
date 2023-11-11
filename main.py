import os, csv
import pandas as pd
from src.scrapper import Scrapper
from src.logger import logging
from datetime import datetime
import threading

THREAD_NUM = 5

def scrape(thread_number: int):
    scrapper = Scrapper()
    scrapper.set_url("https://www.google.com/maps/")
    scrapper.set_timeout(10)
    data = []
    data_path = os.path.join("data","Assignment.xlsx")
    excel_keywords = pd.read_excel(data_path)
    df = pd.DataFrame(excel_keywords)

    file_name = "reviews_"+datetime.now().strftime('%m_%d_%Y_%H_')+thread_number.__str__()+".csv"
    dir_path = os.path.join(os.getcwd(),"extracted_data")
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

        csv_file = open(file_path, 'w')
        if csv_file != None:
            writer = csv.writer(csv_file)
            for index,row in df.iterrows():
                if index%THREAD_NUM == thread_number:
                    new_reviews = scrapper.get_maps_data(row[0])
                    for review in new_reviews:
                        writer.writerow([row[0],row[1],review[0],review[1]])
            csv_file.close()
    except Exception as e:
        logging.critical(e,exc_info=True)

    scrapper.close_scrapper()

# def scrapem(num):
#     for i in range(10):
#         if i%THREAD_NUM == num:
#             print(f'{i}\t{num}')


if __name__ =="__main__":
    thread_count = THREAD_NUM
    threads = list()
    for thread_num in range(thread_count):
        threads.append(threading.Thread(target=scrape, args=(thread_num,)))


    for t in threads:
        t.start()

    for t in threads:
        t.join()

    
