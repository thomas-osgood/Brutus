#!/usr/bin/env python3

import argparse
import os

def attach_multiples(word, amount = None):
    message = str()
    permutations = list()
    success = bool()

    try:
        if (amount is None) or not(isinstance(amount, int)):
            amount = 3
        elif (amount < 2):
            raise ValueError("amount must be >= 2")

        if not(isinstance(word, str)):
            raise ValueError(f"word must be a string. Got {type(word)}")

        for number in range(2,amount+1):
            permutations.append(word * number)

        message = "Multiples successfully added"
        success = True
    except Exception as ex:
        message = str(ex)
        success = False

    return (permutations, success, message)

def attach_numbers(word, start = None, end = None):
    message = str()
    numbered_words = list()
    rmessage = str()
    rsuccess = bool()
    success = bool()

    try:
        if not(isinstance(word,str)):
            raise ValueError(f"word must be a string. Got {type(word)}")

        if (start is None) or not(isinstance(start,int)):
            start = 0

        if (end is None) or not(isinstance(end,int)):
            end = 1000

        start, end, rsuccess, rmessage = validate_range(start, end)

        if not(rsuccess):
            raise ValueError(rmessage)

        for number in range(start,end+1):
            new_word = f"{word}{number}"

            numbered_words.append(new_word)

        message = "Numbered words successfully generated"
        success = True
    except Exception as ex:
        message = str(ex)
        success = False

    return (numbered_words, success, message)

def attach_file(base_file, addon_file):
    message = str()
    success = bool()

    try:
        if not(isinstance(base_file, str)):
            raise ValueError(f"base_file must be a string. Got {type(base_file)}")

        if not(isinstance(addon_file, str)):
            raise ValueError(f"addon_file must be a string. Got {type(addon_file)}")

        with open(base_file, "a") as fptr:
            with open(addon_file,"r") as fptr2:
                for line in fptr2:
                    fptr.write(line)

        success = True
    except Exception as ex:
        message = str(ex)
        success = False

    return (success, message)

def generate_defaults(filename = None, start = None, end = None):
    message = str()
    permutations = list()
    rmessage = str()
    rsuccess = bool()
    success = bool()

    print("[*] Generating Defults")
    if (filename is None) or not(isinstance(filename, str)):
        filename = "_custom_passwords.txt"

    try:
        os.remove("_tmp_numbered")
        print("[+] _tmp_numbered deleted")
    except:
        pass

    try:
        os.remove("_tmp_multiples")
        print("[+] _tmp_multiples deleted")
    except:
        pass

    try:
        os.remove(filename)
        print(f"[+] {filename} deleted")
    except Exception as ex:
        print(f"[-] Error Deleting {filename}:\n\t{str(ex)}")
        pass

    try:
        if (start is None) or not(isinstance(start, int)):
            start = 0

        if (end is None) or not(isinstance(end, int)):
            end = 1000

        base_words = [
                "password",
                "secret",
                "root",
                "toor"
        ]

        print("[*] Generating Base Words")
        for base_word in base_words:
            rpermutations, rsuccess, rmessage = generate_permutations(base_word)

            if not(rsuccess):
                raise ValueError(rmessage)

            with open(filename,"a") as fptr:
                for rpermutation in rpermutations:
                    fptr.write(f"{rpermutation}\n")

            base_word = base_word[::-1]

            rpermutations, rsuccess, rmessage = generate_permutations(base_word)

            if not(rsuccess):
                raise ValueError(rmessage)

            with open(filename,"a") as fptr:
                for rpermutation in rpermutations:
                    fptr.write(f"{rpermutation}\n")

        perm_gen = read_base_gen(filename)
        for perm_cur in perm_gen:
            rpermutations, rsuccess, rmessage = attach_numbers(perm_cur, start=1, end=100)

            if not(rsuccess):
                raise ValueError(rmessage)

            with open("_tmp_numbered","a") as fptr:
                for rpermutation in rpermutations:
                    fptr.write(f"{rpermutation}\n")

        for permutation in read_base_gen(filename):
            rpermutations, rsuccess, rmessage = attach_multiples(permutation,2)
        
            if not(rsuccess):
                raise ValueError(rmessage)
            
            for rpermutation in rpermutations:
                with open("_tmp_multiples","a") as fptr:
                    fptr.write(f"{rpermutation}\n")
        
        rsuccess, rmessage = attach_file(filename, "_tmp_numbered")
        if not(rsuccess):
            raise ValueError(f"Error Attach _tmp_numbered:\n\t{rmessage}")

        rsuccess, rmessage = attach_file(filename, "_tmp_multiples")
        if not(rsuccess):
            raise ValueError(f"Error Attaching _tmp_multiples:\n\t{rmessage}")


        message = f"Default passwords generated and saved to \"{filename}\""
        success = True
    except IOError as ex:
        message = str(ex)
        success = False
    except Exception as ex:
        message = str(ex)
        success = False

    ##############################################
    # Clean up custom, temporary lists generated
    # during the execution of the script.
    ##############################################
    try:
        os.remove("_tmp_numbered")
        print("[+] _tmp_numbered deleted")
    except:
        pass

    try:
        os.remove("_tmp_multiples")
        print("[+] _tmp_multiples deleted")
    except:
        pass
    return (success, message)

def generate_permutations(word):
    permutations = list()
    message = str()
    success = bool()
    tmp_current = str()

    try:
        if not(isinstance(word, str)):
            raise ValueError(f"word must be a string. Got {type(word)}")

        word = word.lower()

        permutations.append(word)
        permutations.append(word.upper())
        permutations.append(word.title())

        # Generate random uppercase/lowercase permutations
        for current in permutations:
            for position in range(len(current)):
                tmp_current = list(current)

                if tmp_current[position].upper() == tmp_current[position]:
                    tmp_current[position] = tmp_current[position].lower()
                elif tmp_current[position].lower() == tmp_current[position]:
                    tmp_current[position] = tmp_current[position].upper()
                else:
                    continue

                tmp_current = "".join(tmp_current)
                
                if not(tmp_current) in permutations:
                    permutations.append(tmp_current)
                else:
                    continue

        message = "Permutations successfully generated"
        success = True
    except Exception as ex:
        message = str(ex)
        success = False

    return (permutations, success, message)

def read_base_gen(filename):
    try:
        if not(isinstance(filename,str)):
            raise ValueError(f"filename must be string. Got {type(filename)}")

        with open(filename) as fptr:
            for line in fptr:
                yield line.strip("\n")
    except Exception as ex:
        return

def validate_range(start, end):
    message = str()
    success = bool()

    try:
        if not(isinstance(start, int)):
            raise ValueError(f"start must be an integer. Got {type(start)}")
        elif start < 0:
            raise ValueError(f"start must be >= 0.")

        if not(isinstance(end, int)):
            raise ValueError(f"end must be an integer. Got {type(end)}")
        elif end < 0:
            raise ValueError(f"end must be >= 0.")

        tmp_start = start

        if start > end:
            start = end
            end = tmp_start
            message = "start and end corrected"
        else:
            message = "start and end valid"

        success = True
    except Exception as ex:
        message = str(ex)
        success = False

    return (start, end, success, message)

def main():
    message = str()
    success = bool()
    words = list()

    try:
        success, message = generate_defaults()

        if not(success):
            raise ValueError(message)

        print(f"[+] {str(message)}")
    except Exception as ex:
        print(f"[-] ERROR: {str(ex)}")

    return

if __name__ == "__main__":
    main()
