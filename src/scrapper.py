import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from src.logger import logging
from src.exception import error_message_details

class Scrapper:
    def __init__(self,url: str = None) -> None:
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.set_url(url)
        self.set_timeout()

    def set_url(self, url: str) -> None:
        self.url = url

    def set_timeout(self,timeout=4):
        self.timeout = timeout
    
    def busy_wait_till_page_load(self,delay = 2):
        try:
            while(self.driver.execute_script('return document.readyState;') != 'complete'):
                time.sleep(delay)
        except Exception as e:
            logging.error(error_message_details(e,sys))

    def get_maps_data(self,keywords:str):
        data = None
        if self.url==None:
            self.url = "https://www.google.com/maps/"
            self.set_url(self.url)
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.busy_wait_till_page_load(4)

        title = self.driver.title
        logging.info(f"""Title of page opened: "{title}".\tKeywords Searched: "{keywords}".""")
        self.timeout = 5
        try:
            element_present = EC.presence_of_element_located((By.ID, 'searchboxinput'))
            WebDriverWait(self.driver, self.timeout).until(element_present)
        except TimeoutException:
            logging.info("Timed out waiting for maps web page to load")
            return data
        except Exception as e:
            logging.error(error_message_details(e,sys))
            return data

        # searchboxinput - id
        # searchboxinput xiQnY - class
        search_box = self.driver.find_element(by=By.ID,value="searchboxinput")

        # id : searchbox-searchbutton
        search_button = self.driver.find_element(by=By.ID, value="searchbox-searchbutton")

        search_box.send_keys(keywords)
        search_button.click()
        data,_ = self.__get_reviews(self.timeout+3)
        return data

    def close_scrapper(self):
        self.driver.quit()
    
    def __get_reviews(self,timeout = 0):
        reviews = list()
        scrollable_page = None
        # review button id :"hh2c6 "
        try:
            element_present = EC.presence_of_element_located((By.XPATH,"""//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[contains(.,'Reviews')]"""))
            WebDriverWait(self.driver, self.timeout).until(element_present)
            

            # review_button = self.driver.find_element(By.CLASS_NAME, "hh2c6 ")
            review_button = self.driver.find_element(By.XPATH,"""//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[contains(.,'Reviews')]""")

            review_button.click()

            try:
                # scrollable object //-----------------------------
                sc_obj_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'

                scroll_element_present = EC.presence_of_element_located((By.XPATH,sc_obj_xpath))
                WebDriverWait(self.driver, self.timeout).until(scroll_element_present)

                scrollable_page = self.driver.find_element(by=By.XPATH,value=sc_obj_xpath)

                reviews.extend(self.__extract_reviews_from_scroll_div(scrollable_page,self.timeout))

            except TimeoutException:
                logging.info("Timed out waiting for Scrollable div to load")
                return reviews, scrollable_page
            except Exception as e:
                logging.error(error_message_details(e,sys))
                return reviews, scrollable_page
        except TimeoutException:
            logging.info("Timed out waiting for review button to load")
            try:
                reviews.extend(self.__select_property_from_scroll_div())
                # print(self.__collect_property_list_from_scroll_div_and_get_reviews())
                return reviews, scrollable_page
            except Exception:
                logging.info("No reviews extracted")
                return reviews, scrollable_page
        except Exception as e:
            logging.error(error_message_details(e,sys))
            return reviews, scrollable_page
        
        return reviews, scrollable_page
    
    def __extract_reviews_from_scroll_div(self,scrollable_page,timeout = 4):
        reviews = list()

        prev_count = -1
        count = 0
        empty_review = 0
        # last_height = self.driver.execute_script("return arguments[0].scrollHeight",scrollable_page)
        while prev_count!=count:
            try:
                prev_count = count
                div_number = 9
                try:
                    if count == 0:
                        review_div_summary_present = EC.presence_of_element_located((By.XPATH,f".//div[8]"))
                        WebDriverWait(scrollable_page, timeout).until(review_div_summary_present)
                        review_summary = scrollable_page.find_element(By.XPATH,f".//div[8]")
                        self.driver.execute_script("arguments[0].scrollIntoView(true); arguments[1].scrollBy(0,arguments[0].scrollHeight)", review_summary,scrollable_page)
                    review_div_present = EC.presence_of_element_located((By.XPATH,f".//div[9]/div[{count*3 + 1}]"))
                    WebDriverWait(scrollable_page, timeout).until(review_div_present)
                except TimeoutException:
                    div_number = 8
                    review_div_present = EC.presence_of_element_located((By.XPATH,f".//div[8]/div[{count*3 + 1}]"))
                    WebDriverWait(scrollable_page, timeout).until(review_div_present)
                

                review_div = scrollable_page.find_element(By.XPATH,f"//div[{div_number}]/div[{count*3 + 1}]")

                #scroll line ----------------------------------------------------------------------------------------------------------------
                self.driver.execute_script("arguments[0].scrollIntoView(true);", review_div)
                # new_height = self.driver.execute_script("return arguments[0].scrollHeight",scrollable_page)
                name_element = None
                try:
                    name_present = EC.presence_of_all_elements_located((By.XPATH,".//div/div/div[2]/div[2]/div[1]/button/div[1]"))
                    WebDriverWait(review_div, timeout).until(name_present)

                    name_element = review_div.find_element(By.XPATH,".//div/div/div[2]/div[2]/div[1]/button/div[1]")

                    review_present = EC.presence_of_all_elements_located((By.XPATH,".//div/div/div[4]/div[2]/div/span[1]"))
                    WebDriverWait(review_div, timeout).until(review_present)

                    review_element = review_div.find_element(By.XPATH,".//div/div/div[4]/div[2]/div/span[1]")
                    try:
                        more_present = EC.presence_of_all_elements_located((By.XPATH,".//parent::div/span[2]/button"))
                        WebDriverWait(review_div, 4).until(more_present)
                        more_button = review_element.find_element(By.XPATH,".//parent::div/span[2]/button")
                        more_button.click()
                        time.sleep(1)
                    except Exception:
                        pass
                    reviews.append((name_element.text, review_element.text))
                except TimeoutException:
                    # empty_review += 1
                    if name_element != None:
                        logging.info(f"Review by {name_element.text} is empty")
                        reviews.append((name_element.text,''))
                    continue

                count += 1

                #scroll line ----------------------------------------------------------------------------------------------------------------
                self.driver.execute_script("arguments[0].scrollBy(0,arguments[1].scrollHeight)",scrollable_page,review_div)


                ### These are comments: --------------------------------------------------------------------------------------------
                # self.driver.execute_script("arguments[0].scrollBy(0,100)",scrollable_page)
                # self.driver.execute_script("arguments[0].scrollBy(0,arguments[0].scrollHeight)",scrollable_page)
                # new_height = self.driver.execute_script("return arguments[0].scrollHeight",scrollable_page)
                ###--------------------------------------------------------------------------------------------

                # print(f"{new_height}")
                # if new_height == last_height:
                #     print("Breaking")
                #     break
                # last_height = new_height
            except Exception as e:
                if count>0:
                    logging.info("No more reviews found")
                else:
                    logging.error(error_message_details(e,sys))
                break

        logging.info(f"{count} reviews extracted.")

        return reviews
  
    def __collect_property_list_from_scroll_div_and_get_reviews(self,start_div_num=1,timeout = 3):
        logging.info("Attempting to get detect property list and get reviews.")
        properties_list = list()
        prev_prop_count = -1
        property_count = 0

        properties_list_div_present = EC.presence_of_all_elements_located((By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'))
        WebDriverWait(self.driver, timeout).until(properties_list_div_present)
        properties_list_div = self.driver.find_element(By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
        property_flag = 0
        while prev_prop_count != property_count or property_flag < 3 :
            prev_prop_count = property_count
            try:
                count = property_count
                property_flag += 1
                property_div_present = EC.presence_of_element_located((By.XPATH,f".//div[{count*2 + start_div_num}]/div/a"))
                WebDriverWait(properties_list_div, timeout).until(property_div_present)
                property_div = properties_list_div.find_element(By.XPATH,f".//div[{count*2 + 1}]/div/a")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", property_div)
                prop_link = property_div.get_attribute('href')
                properties_list.append(prop_link)
                property_count += 1
                self.driver.execute_script("arguments[0].scrollBy(0,arguments[1].scrollHeight)",properties_list_div,property_div.parent)
            except TimeoutException:
                if property_flag >=2 :
                    logging.info("Unable to find more properties in the list.")
                logging.info(f"property list :\t{properties_list}")
                return properties_list
            except Exception as e:
                logging.error(error_message_details(e,sys))
                return properties_list
            # for property in properties_list:
            #     # open property link and get reviews
            #     pass

        return properties_list

            

        
    def __select_property_from_scroll_div(self,timeout = 3):
        logging.info("Attempting to get detect property list and get reviews.")
        reviews = list()
        property_list = []
        try:
            property_list.extend(self.__collect_property_list_from_scroll_div_and_get_reviews())
        except Exception:
            pass
        try:
            property_list.extend(self.__collect_property_list_from_scroll_div_and_get_reviews(0))
        except Exception:
            pass

        for property in property_list:
            try:
                self.driver.execute_script(f'''window.open("{property}","_blank");''')
                self.driver.switch_to.window(self.driver.window_handles[1])
                # scrape reviews from page
                # scrollable_review_page_present = EC.presence_of_all_elements_located((By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]'))
                # WebDriverWait(self.driver, timeout).until(scrollable_review_page_present)
                # scrollable_review_page = self.driver.find_element(By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]')
                # reviews.extend(self.__extract_reviews_from_scroll_div(scrollable_review_page,timeout+4))
                self.__get_reviews(timeout+3)
                #..........................
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception as e:
                self.driver.switch_to.window(self.driver.window_handles[0])
                logging.error(error_message_details(e,sys))

        return reviews
        # prev_count = -1
        # count = 0

        # properties_list_div_present = EC.presence_of_all_elements_located((By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'))
        # WebDriverWait(self.driver, timeout).until(properties_list_div_present)
        # properties_list_div = self.driver.find_element(By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')

        # while prev_count != count:
        #     prev_count = count
        #     try:
        #         property_div_present = EC.presence_of_element_located((By.XPATH,f".//div[{count*2 + 1}]/div/a"))
        #         WebDriverWait(properties_list_div, timeout).until(property_div_present)
        #         property_div = properties_list_div.find_element(By.XPATH,f".//div[{count*2 + 1}]/div/a")

        #         property_div.click()

        #         preperty_details_div_present = EC.presence_of_all_elements_located((By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]'))
        #         WebDriverWait(self.driver, timeout).until(preperty_details_div_present)
        #         preperty_details_div = self.driver.find_element(By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]')

        #         review_page_button_present = EC.presence_of_all_elements_located((By.XPATH,".//div[3]/div/div/button[contains(.,'Reviews')]"))
        #         WebDriverWait(preperty_details_div, timeout).until(review_page_button_present)
        #         review_page_button = preperty_details_div.find_element(By.XPATH,".//div[3]/div/div/button[contains(.,'Reviews')]")
        #         review_page_button.click()

                # scrollable_review_page_present = EC.presence_of_all_elements_located((By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]'))
                # WebDriverWait(preperty_details_div, timeout).until(scrollable_review_page_present)
                # scrollable_review_page = preperty_details_div.find_element(By.XPATH,'/html/body/div[3]/div[8]/div[9]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]')
                # reviews.extend(self.__extract_reviews_from_scroll_div(scrollable_review_page,timeout+4))
        #         count+=1

        #     except TimeoutException:
        #         logging.info("Unable to find more properties in the list.")
        #     except Exception as e:
        #         logging.error(error_message_details(e,sys))
        


if __name__ == "__main__":
    import pandas as pd
    import os
    scrapper = Scrapper()
    scrapper.set_url("https://www.google.com/maps/")
    data = []
    data_path = os.path.join("data","Assignment.xlsx")
    excel_keywords = pd.read_excel(data_path)
    df = pd.DataFrame(excel_keywords)    
    for index,row in df.iterrows():
        new_reviews = scrapper.get_maps_data(row[0])
        print(new_reviews)


    scrapper.close_scrapper()





