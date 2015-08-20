__author__ = 'Timothy Portfolio'

'''To-Do List'''
# remove users that the HTML mistakenly leaves in the roster (i.e. Guests in member/recruit list)
# add hyperlinks to the profiles?
# parse the hyperlinks and check dates there too?
# turn this into a .exe with GUI

'''Imports and Globals'''


from bs4 import BeautifulSoup
import requests
import datetime

parse_veterans = False #toggle on/off depending on needs
today = datetime.date.today()

'''Auxiliary Functions'''


def invalid_tokens(date, vet_array):
    if ("Today" in date or "Yesterday" in date or
                "Online" in date or "minutes" in date):
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


'''Main Code'''


def main():
    page = requests.get('http://hellsgamers.com/roster.html')
    html = page.content

    soup = BeautifulSoup(html, "lxml") #added the "lxml" argument to remove warning on interpretation

    users = soup.findAll('table', attrs={'class': 'ipb_table ipsMemberList'}) #retrieves all tables

    if parse_veterans:
        veterans = users[5].findAll('tr', {'class': ['row2', 'row1']}) #html alternates the style
        print("\nVeterans")
        i = 0
        while i < len(veterans):
            tdelements = veterans[i].findAll('td') #the name and last active date are embedded
            name = tdelements[1].text.replace('\n', '').replace('\t', '')
            date = tdelements[5].text.replace('\n', '').replace('\t', '').split('-',1)[0] #remove hour
            if not(invalid_tokens(date, True)):
                print(name + " - " + date)
            i+=1

    members = users[6].findAll('tr', {'class': ['row2', 'row1']})
    print("\nMembers")
    i = 0
    while i < len(members):
        tdelements = members[i].findAll('td')
        name = tdelements[1].text.replace('\n', '').replace('\t', '')
        date = tdelements[5].text.replace('\n', '').replace('\t', '').split('-',1)[0]
        if not(invalid_tokens(date, False)):
            day = int(date.split(' ',2)[0])
            month = date.split(' ',2)[1]
            year = int(date.split(' ',2)[2])
            diff = today - datetime.date(year, abbr_to_num(month), day)
            if diff.days >= 90:
                print(name + " - " + str(diff.days) + " days")
        i += 1

    recruits = users[7].findAll('tr', {'class': ['row2', 'row1']})
    print("\nRecruits")
    i = 0
    while i < len(recruits):
        tdelements = recruits[i].findAll('td')
        name = tdelements[1].text.replace('\n', '').replace('\t', '')
        date = tdelements[5].text.replace('\n', '').replace('\t', '').split('-',1)[0]
        if not(invalid_tokens(date, False)):
            day = int(date.split(' ',2)[0])
            month = date.split(' ',2)[1]
            year = int(date.split(' ',2)[2])
            diff = today - datetime.date(year, abbr_to_num(month), day)
            if diff.days >= 60:
                print(name + " - " + str(diff.days) + " days")
        i += 1

if __name__ == "__main__":
    main()
