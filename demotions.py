__author__ = 'Timothy Portfolio'

'''To-Do List'''

# turn this into a .exe with GUI

'''Imports and Globals'''


import datetime
from selenium import webdriver
import time

parse_veterans = False #toggle on/off depending on needs
full_demotion_process = False #toggle on/off depending on needs
today = datetime.date.today()

'''Auxiliary Functions'''


def invalid_tokens(date, vet_array):
    if ("Today" in date or "Yesterday" in date or
                "Online" in date or "ago" in date): #i.e. "A minute ago", "5 minutes ago"
        return True
    elif vet_array and ("2014" in date or "2015" in date):
        return True
    else:
        return False

def abbr_to_num(abbr):
    return {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
    }[abbr]

def index_num(rank):
    return {
        "Veteran": 4, "Member": 5, "Recruit": 6,
    }[rank]

def add_note(browser):

    browser.find_element_by_partial_link_text("Demote").click()
    browser.find_element_by_partial_link_text("Member Note").click()
    browser.find_element_by_link_text("Add Note").click()
    time.sleep(3)
    note_field = browser.find_element_by_class_name("input_text")
    note_field.send_keys("Demoted for forum inactivity - <insert thread here>")
    browser.find_element_by_class_name("input_submit").click()
    time.sleep(2)

def demoter(browser, usernames_and_links, rank):
    demoted_names = []
    i = 0
    while i < len(usernames_and_links):
        browser.get(usernames_and_links[i][1])
        span_list = browser.find_elements_by_css_selector(".desc.lighter")
        last_active = ""
        for el in span_list:
            if "Last Active" in el.text:
                last_active = el.text.replace("Last Active ", "")
                break
        if rank is not "Veteran":
            if not(invalid_tokens(last_active, False)):
                inactivity_length = 90 if rank == "Member" else 60
                try:
                    day = int(last_active.split(' ',3)[1])
                    month = last_active.split(' ',3)[0]
                    year = int(last_active.split(' ',3)[2])
                    diff = today - datetime.date(year, abbr_to_num(month), day)
                    if diff.days >= inactivity_length:
                        print(usernames_and_links[i][0] + " - " + str(diff.days) + " days" + " - " + usernames_and_links[i][1])
                        demoted_names.append(usernames_and_links[i][0])
                        if full_demotion_process:
                            add_note(browser)
                except:
                    print(usernames_and_links[i][0] + " - (private) - " + " - " + usernames_and_links[i][1])
                    demoted_names.append(usernames_and_links[i][0])
                    if full_demotion_process:
                        add_note(browser)

        else:
            if not(invalid_tokens(last_active, True)):
                print(usernames_and_links[i][0] + " - " + last_active + " - " + usernames_and_links[i][1])
                demoted_names.append(usernames_and_links[i][0])
                if full_demotion_process:
                    add_note(browser)
        i+=1
    sorted(demoted_names, key=lambda s: s.lower())
    for el in demoted_names:
        print(el)

def user_parser(browser, rank):

    browser.get('http://hellsgamers.com/roster.html')
    tables = browser.find_elements_by_tag_name("table")
    index = index_num(rank)
    usernames_and_links = []
    user_trs = tables[index].find_elements_by_class_name("row1")
    user_trs + tables[index].find_elements_by_class_name("row2")

    i = 0
    while i < len(user_trs):
        #print(el.get_attribute('innerHTML'))
        tdelements = user_trs[i].find_elements_by_tag_name('td')
        name = tdelements[1].text.replace('\n', '').replace('\t', '')
        date = tdelements[5].text.replace('\n', '').replace('\t', '').split('-',1)[0] #remove hour

        if rank is "Veteran":
            if not(invalid_tokens(date, True)):
                link = user_trs[i].find_element_by_tag_name('a').get_attribute('href')
                #print(name + " - " + date + " - " + link)
                new_tuple = (name, link)
                usernames_and_links.append(new_tuple)
        else:
            if not(invalid_tokens(date, False)):
                inactivity_length = 90 if rank == "Member" else 60
                day = int(date.split(' ',2)[0])
                month = date.split(' ',2)[1]
                year = int(date.split(' ',2)[2])

                diff = today - datetime.date(year, abbr_to_num(month), day)
                if diff.days >= inactivity_length:
                    link = user_trs[i].find_element_by_tag_name('a').get_attribute('href')
                    #print(name + " - " + str(diff.days) + " days" + " - " + link)
                    new_tuple = (name, link);
                    usernames_and_links.append(new_tuple)
        i+=1
    demoter(browser, usernames_and_links, rank)

'''Main Code'''


def main():

    browser = webdriver.Firefox()
    browser.get('http://hellsgamers.com/')
    browser.find_element_by_id("sign_in").click()
    time.sleep(3)
    username = browser.find_element_by_id("ips_username")
    password = browser.find_element_by_id("ips_password")
    username.send_keys("") #personal info redacted
    password.send_keys("") #personal info redacted
    browser.find_element_by_class_name("input_submit").click()

    if parse_veterans:
        print("Veterans")
        user_parser(browser, "Veteran")

    print("\nMembers")
    user_parser(browser, "Member")
    print("\nRecruits")
    user_parser(browser, "Recruit")
    '''links = ["http://hellsgamers.com/user/30659-13percent/", "http://hellsgamers.com/user/30659-13percent/"]
    names = ["13Percent", "13Percent"]
    rank = "Member"
    demoter(browser, links, names, rank)'''


if __name__ == "__main__":
    main()
