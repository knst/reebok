#!/usr/bin/env python3

import http.client, urllib
import re
import sys
import time

def sendMessage(token, user, message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": token,
        "user": user,
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    response = conn.getresponse()

    print(response.status, response.reason)

    data = response.read()
    print(len(data))
    print(data)


def getToken(file):
    tokenFile = open(file)
    token = tokenFile.read()
    return token.strip()

def main():
    user_token = getToken(".user-key")
    app_token = getToken(".app-key")
    site_cookie = getToken(".site-cookie")
    print("tokens: ", user_token, app_token, site_cookie)

    date = "2015-07-27"

    # state:
    #   -4: start
    #   -3: error
    #   -2: empty
    #   -1: no 50 years
    #   0+: count in 50 years
    state = -4
    while (True):
        conn = http.client.HTTPConnection("www.reebokinparks.com")
        conn.request("GET", "/workouts/register/?date=" + date, headers = { "Cookie" : site_cookie });
        response = conn.getresponse()
        print("Reebok: ", response.status, response.reason)

        sleepTime = 600
        newState = -1
        if response.status == 200:
            data = response.read().decode('utf-8')
            print("len of data: ", len(data))

            newState = -1

            searchFilled = "<p>Свободных мест на этот день больше нет!</p>"
            sFilled = re.search(searchFilled, data)

            if sFilled:
                newState = -2

            searchEmpty = "<strong>50-летия Октября</strong>,\n.*\n.*осталось мест &mdash; <strong>([0-9]*)</strong>"
            sEmpty = re.search(searchEmpty, data)
            if sEmpty:
                newState = int(sEmpty.group(1))

            if newState != state:
                sleepTime = 60
            print("state: ", state, " --> ", newState)
            if (state != newState and newState > 0) or state == -4:
                sendMessage(app_token, user_token, "Check reebok! " + str(newState) + " in 50 years")
            state = newState
        else:
            state = -3

        time.sleep(sleepTime)



if __name__ == "__main__":
    sys.exit(main())
