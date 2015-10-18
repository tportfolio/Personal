__author__ = 'Timothy Portfolio'

'''To-Do List'''

# turn this into a .exe with GUI
# improve
# multi-threading possible with workerpool module?
# better integration with retired leadership/permanent veterans

'''Imports and Globals'''

import datetime
from selenium import webdriver
import time

parse_veterans = False # toggle on/off depending on needs
full_demotion_process = True # toggle on/off depending on needs
today = datetime.date.today()
ignore_list = ["Finn :D"]

'''Auxiliary Functions'''

class Parser(object):

    def index_num(self, rank):
        return {
            "Veteran": 4, "Member": 5, "Recruit": 6,
        }[rank]

    def invalid_tokens(self, date, vet_array):
        if ("Today" in date or "Yesterday" in date or
                    "Online" in date or "ago" in date): #i.e. "A minute ago", "5 minutes ago"
            return True
        elif vet_array and ("2014" in date or "2015" in date):
            return True
        else:
            return False

    def abbr_to_num(self, abbr):
        return {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
        }[abbr]

class UserProfile(object):

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

class Browser(object):

    browser = webdriver.Firefox()
    parser = Parser()

    def __init__(self):
        self.browser.get('http://hellsgamers.com/')

    def goto(self, link):
        self.browser.get(link)

    def login(self):
        self.browser.find_element_by_id("sign_in").click()
        time.sleep(3)
        username = self.browser.find_element_by_id("ips_username")
        password = self.browser.find_element_by_id("ips_password")
        username.send_keys("") #redacted
        password.send_keys("") #redacted
        self.browser.find_element_by_class_name("input_submit").click()

    def find_tables(self, rank):
        tables = self.browser.find_elements_by_tag_name("table")
        index = self.parser.index_num(rank)
        user_tr1 = tables[index].find_elements_by_class_name("row1")
        user_tr2 = tables[index].find_elements_by_class_name("row2")
        return user_tr1 + user_tr2

    def find_spans(self, link):
        self.browser.get(link)
        return self.browser.find_elements_by_css_selector(".desc.lighter")

    def add_note(self):
        self.browser.find_element_by_partial_link_text("Demote").click()
        self.browser.find_element_by_partial_link_text("Member Note").click()
        self.browser.find_element_by_link_text("Add Note").click()
        time.sleep(3)
        note_field = self.browser.find_element_by_class_name("input_text")
        note_field.send_keys("Test 5: Revenge of the Test")
        self.browser.find_element_by_class_name("input_submit").click()
        time.sleep(2)


class Scraper(object):

    def __init__(self, browser, rank):
        self.browser = browser
        self.rank = rank

    def collect(self):
        parser = Parser()
        self.browser.goto('http://hellsgamers.com/roster.html')
        tables = self.browser.find_tables(self.rank)
        users = []
        i = 0
        while i < len(tables):
            # print(el.get_attribute('innerHTML'))
            tdelements = tables[i].find_elements_by_tag_name('td')
            name = tdelements[1].text.replace('\n', '').replace('\t', '')
            date = tdelements[5].text.replace('\n', '').replace('\t', '').split('-',1)[0] #remove hour

            if self.rank is "Veteran":
                if not(parser.invalid_tokens(date, True)):
                    link = tables[i].find_element_by_tag_name('a').get_attribute('href')
                    # print(name + " - " + date + " - " + link)
                    user = UserProfile(name, link)
                    users.append(user)
            else:
                if not(parser.invalid_tokens(date, False)):
                    inactivity_length = 90 if self.rank == "Member" else 60
                    day = int(date.split(' ',2)[0])
                    month = date.split(' ',2)[1]
                    year = int(date.split(' ',2)[2])

                    diff = today - datetime.date(year, parser.abbr_to_num(month), day)
                    if diff.days >= inactivity_length:
                        link = tables[i].find_element_by_tag_name('a').get_attribute('href')
                        # print(name + " - " + str(diff.days) + " days" + " - " + link)
                        user = UserProfile(name, link)
                        users.append(user)
            i+=1
        return users

class Demoter(object):

    def __init__(self, browser, profiles, rank):
        self.browser = browser
        self.profiles = profiles
        self.rank = rank

    def verify(self):
        demoted_names = []
        parser = Parser()

        i = 0
        while i < len(self.profiles):
            time.sleep(2)
            span_list = self.browser.find_spans(self.profiles[i].get_url())
            last_active = ""
            for el in span_list:
                if "Last Active" in el.text:
                    last_active = el.text.replace("Last Active ", "")
                    break
            if self.rank is not "Veteran":
                if not(parser.invalid_tokens(last_active, False)) and self.profiles[i].get_name() not in ignore_list:
                    inactivity_length = 90 if self.rank == "Member" else 60
                    try:
                        day = int(last_active.split(' ',3)[1])
                        month = last_active.split(' ',3)[0]
                        year = int(last_active.split(' ',3)[2])
                        diff = today - datetime.date(year, parser.abbr_to_num(month), day)

                        if diff.days >= inactivity_length:
                            if self.rank == "Member":
                                ignore_list.append(self.profiles[i].get_name()) #avoid double demotion

                            print(self.profiles[i].get_name() + " - " + str(diff.days) + " days" + " - " + self.profiles[i].get_url())
                            demoted_names.append(self.profiles[i].get_name())
                            if full_demotion_process:
                                self.browser.add_note()
                    except:
                        print(self.profiles[i].get_name() + " - (private) - " + " - " + self.profiles[i].get_url())
                        demoted_names.append(self.profiles[i].get_name())
                        if full_demotion_process:
                            self.browser.add_note()

            else:
                if not(parser.invalid_tokens(last_active, True)) and self.profiles[i].get_name() not in ignore_list:
                    print(self.profiles[i].get_name() + " - " + last_active + " - " + self.profiles[i].get_url())
                    demoted_names.append(self.profiles[i].get_name())
                    if full_demotion_process:
                        self.browser.add_note()
            i+=1
        demoted_names = sorted(demoted_names, key=lambda s: s.lower())
        for el in demoted_names:
            print(el)

'''Main Code'''

def main():

    browser = Browser()
    browser.login()
    scraper = Scraper(browser, "Member")
    users = scraper.collect()
    for el in users:
        print(el.get_name() + ' - ' + el.get_url())
    demoter = Demoter(browser, users, "Member")
    demoter.verify()


if __name__ == "__main__":
    main()
