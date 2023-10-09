import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import datetime
import time
import re 

import pickle

from ticket import Ticket, PrizesRemaining

from logger import get_logger

import logging
logger = get_logger(__name__)
logger.setLevel(logging.INFO)

pattern = re.compile(r'\s+')
class ScrapeMD(object):
    def __init__(self):
        self.site = 'Maryland Lottery'
        self.file_name = 'html/betus.html'
        self.url = 'https://www.mdlottery.com/games/scratch-offs/'


    def _get_html(self):
        logger.info("Starting betUS")
        options = webdriver.ChromeOptions()
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        
        chromedriver_path = "chromedriver.exe" # https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.132/win64/chrome-win64.zip

        driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        print("get url")
        driver.get(self.url)
        #TODO fix later
        random_backoff = 3
        time.sleep(random_backoff)
        start = time.time()
        print("START doing someting")
        ticket_list_class = "tickets"
        ticket_list = driver.find_element_by_class_name(ticket_list_class)
        ticket_class = "ticket"
        ticket_boxes = ticket_list.find_elements_by_class_name(ticket_class)
        print("clicking the cookies away...")
        cookie_link = driver.find_element(By.LINK_TEXT, 'Use necessary cookies only')
        cookie_link.click()
        # driver.fin
        list_of_tickets = []
        x = 0
        for ticket in ticket_boxes:
            # x += 1
            # print(ticket.text, flush=True)

            # get all the data
            # selenium is obstinate and wont let me use get by class name
            price = ticket.find_element_by_class_name("price").text
            name = ticket.find_element_by_class_name("name").text
            info = ticket.find_element_by_class_name("info")

            # TODO update ot class names later if needed
            top_prize = ticket.find_element_by_css_selector("div.info > ul.primary > li:nth-child(1) > strong").text
            remaining_top_prizes = ticket.find_element_by_css_selector("div.info > ul.primary > li:nth-child(2) > strong").text
            chances_to_win = ticket.find_element_by_css_selector("div.info > ul.primary > li:nth-child(3) > strong").text
            game_start_date = ticket.find_element_by_css_selector("div.info > ul.primary > li:nth-child(4) > strong").text
            # if there are 6 children then the 5th is the last date to claim, and 6th is probablity
            if len(ticket.find_elements_by_css_selector("div.info > ul.primary > li")) == 6:
                last_date_to_claim = ticket.find_element_by_css_selector("div.info > ul.primary > li:nth-child(5) > strong").text
                probability = ticket.find_element_by_css_selector("div.info > ul.primary > li:nth-child(6) > strong").text
            else:
                last_date_to_claim = None
                probability = ticket.find_element_by_css_selector("div.info > ul.primary > li:nth-child(5) > strong").text
            
            prize_link = ticket.find_element_by_css_selector("div.info > ul.secondary > li:nth-child(3) > a")
            # click on the link to get the prizes remaining
            link = ticket.find_element(By.LINK_TEXT, 'Prizes Remaining')
            link.click()
            print("click to open")
            prize_pop_up = driver.find_element_by_class_name("prize-details")
            table = prize_pop_up.find_element_by_css_selector("table > tbody")
            # print(table.text)
            time.sleep(random_backoff)
            prizes_remaining_list = []
            for line in table.text.split("\n"):
                try:
                    values = line.split(" ")
                    prize = values[0]
                    start_num = values[1]
                    remaining = values[2]
                    prizes_remaining_list.append(PrizesRemaining(prize, start_num, remaining))
                    
                except:
                    print(f"line did not parse correctly: {line}")
                    pass

            link = prize_pop_up.find_element_by_css_selector('button')
            link.click()
            print("click to close")

            # save remianing prizes in object
            this_ticket = Ticket(name, 
                                 price, 
                                 top_prize, 
                                 remaining_top_prizes, 
                                 chances_to_win, 
                                 game_start_date, 
                                last_date_to_claim,
                                 probability, 
                                 prizes_remaining_list, 
                                None)
            
            
            list_of_tickets.append(this_ticket)
            # print(this_ticket)
            time.sleep(1)
            
            if x > 2:
                break
        driver.close()
        end1 = time.time()

        # driver2 = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        # for ticket_obj in list_of_tickets:
        #     print(ticket_obj.name)
        #     driver2.get(ticket_obj.prizes_remaining_link)
        #     driver2.refresh()
        #     prize_pop_up = driver2.find_element_by_class_name("prize-details")
        #     table = prize_pop_up.find_element_by_css_selector("table > tbody")
        #     # print(table.text)
        #     time.sleep(random_backoff)
        #     for line in table.text.split("\n"):
        #         try:
        #             values = line.split(" ")
        #             prize = values[0]
        #             start_num = values[1]
        #             remaining = values[2]
        #             ticket_obj.prizes_remaining.append(PrizesRemaining(prize, start_num, remaining))
                    
        #         except:
        #             print(f"line did not parse correctly: {line}")
        #             pass
        # print(list_of_tickets)
        # with open(self.file_name, "w") as f:
        #     f.write(driver.page_source)#.replace('\ufffd', ''))
        # driver2.close()

        
        # wirte the list of ticket to a pickle file
        with open("tickets.pkl", "wb") as f:
            pickle.dump(list_of_tickets, f)
        end2 = time.time()
        print(f"end1-start={end1-start}")
        print(f"end2-end1={end2-end1}")
        print(f"end2-start={end2-start}")
        print(f"{len(list_of_tickets)}=")
if __name__ == "__main__":
    scraper = ScrapeMD()
    scraper._get_html()