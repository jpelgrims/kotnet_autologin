import requests
import math
import time
import logging

username = ""
password = ''
email = ""
ip_addresses = []

domain = "https://netlogin.kuleuven.be"
login_prompt_url = "/cgi-bin/wayf2.pl?inst=kuleuven&lang=nl&submit=Ga+verder+%2F+Continue"
logout_prompt_url = "/cgi-bin/wayf2.pl"
login_form_url = "/cgi-bin/netlogin.pl"
logout_form_url = "/cgi-bin/netlogout.pl"

headers = {"User-Agent": "KotnetAutoLogin 0.1", 
           "From": email}

def is_kotnet_up():
    try:
        response = requests.get(domain + login_prompt_url, headers=headers)
    except:
        return False 
    if response.status_code is 200:
        return True
    else:
        return False

def is_internet_up():
    try:
        response = requests.get("http://www.google.com", timeout=5)
    except:
        return False
    if response.status_code is 200 and not "Log in aub" in response.text:
        return True
    else:
        return False

def parse_pwd_parameter(response):
    # Find correct password parameter, is "pwd" + some seemingly random/increasing number that can be 1 to 5 digits large
    start = response.text.find("pwd")
    end = response.text.find('"', start, len(response.text))
    pwd_parameter = response.text[start: end]
    return pwd_parameter

def parse_volume_left(response):
    # Find available download bytes
    hook = "weblogin: available download = "
    start = response.text.find(hook) + len(hook)
    end = response.text.find(' of ', start, len(response.text))
    download = int(response.text[start: end]) * math.pow(10, -9)

    # Find available upload bytes
    hook = "weblogin: available upload = "
    start = response.text.find(hook) + len(hook)
    end = response.text.find(' of ', start, len(response.text))
    upload = int(response.text[start: end]) * math.pow(10, -9)

    return download, upload

def login():
    response = requests.get(domain + login_prompt_url, headers=headers)
    pwd_parameter = parse_pwd_parameter(response)
    response = requests.post(domain + login_form_url, 
                             headers=headers,
                             data = {'uid': username,
                                     'inst': 'kuleuven',
                                     'lang': 'nl',
                                     'submit': 'Login',
                                     pwd_parameter: password})
    if "Login geslaagd" in response.text:
        return True
    else:
        return False

def logout(ip_address):
    response = requests.post(domain + logout_prompt_url, 
                             headers=headers, 
                             data= {'inout': "logout",
                                    'ip': ip_address,
                                    'network': 'KotNet',
                                    'uid': "kuleuven/" + username,
                                    'lang': 'ned'})
    pwd_parameter = parse_pwd_parameter(response)
    response = requests.post(domain + logout_form_url, 
                             headers=headers, 
                             data = {'uid': username,
                             pwd_parameter: password,
                             'ip': ip_address,
                             'inst': 'kuleuven',
                             'lang': 'nl',
                             'submit': 'Logout'})
    if "Logout geslaagd" in response.text:
       return True
    elif "rc=207" in response.text:
        # IP address not logged in
        return True
    else:
        return False

def run():
    while True:
        if not is_internet_up() and is_kotnet_up():
            print("Authenticating...")
            if not login():
                for ip_address in ip_addresses:
                    logout(ip_address)
                    if login():
                        break
            if is_internet_up():
                print("Kotnet authentication succesfull!")
            else:
                print("Kotnet authentication failed.")
        time.sleep(60)

if __name__ == "__main__":
    run()
