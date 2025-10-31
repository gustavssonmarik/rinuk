import urllib.parse
import string
import secrets
import logging
import time
import requests
from seleniumbase import SB
import os
import random 
import json
from pymongo import MongoClient
from selenium.webdriver.common.keys import Keys
import types
import sys
from datetime import datetime, timedelta
import ast
import re
import base64
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
MONGO_U = "bW9uZ29kYitzcnY6Ly90cm9jdXBvY3U6QkU1ZkVTVEZNajBUZE8yUUBjaGF0ZGF0YS5ybXRzZmQ1Lm1vbmdvZGIubmV0Lz9yZXRyeVdyaXRlcz10cnVlJnc9bWFqb3JpdHkmYXBwTmFtZT1jaGF0ZGF0YQ=="
decoded_bytes = base64.b64decode(MONGO_U)
MONGO_URI = decoded_bytes.decode("utf-8")
def unlock_expired_documents():
    """
    This function connects to MongoDB Atlas and checks the oauth collection for any documents that
    have been locked for more than 3 hours. For such documents, it resets is_locked to False (and
    optionally removes the locked_at field).
    """
    try:
        client = MongoClient(MONGO_URI,tls=True,tlsAllowInvalidCertificates=True)
        db = client["trocu"]
        collection = db["cookiesk"]

        # Calculate the cutoff timestamp (3 hours ago from now).
        cutoff_time = datetime.utcnow() - timedelta(hours=123)
        logging.info("Running scheduled unlock: unlocking documents locked before %s", cutoff_time)

        query = {
            "is_locked": True,
            "locked_at": {"$lte": cutoff_time}
        }
        update = {
            "$set": {"is_locked": False},
            "$unset": {"locked_at": ""}  # Remove locked_at field
        }

        result = collection.update_many(query, update)
        logging.info("Scheduled unlock: Unlocked %d document(s)", result.modified_count)
    except Exception as e:
        logging.error("Error in scheduled unlock: %s", e)
    finally:
        client.close()

def delete_entry(query):
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["trocu"]
        collection = db["cookiesk"]
        
        result = collection.delete_one({"cookies": query})
        if result.deleted_count > 0:
            print(f"Successfully deleted 1 document matching {query}.")
        else:
            print("No matching document found to delete.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
def retrieve_and_lock_random_cookie():
    """
    Connects to the 'trocu' database and retrieves one random document from the
    'cookiesk' collection where is_locked is False. Once a document is found,
    it prints the 'cookies' field and updates the document by setting is_locked
    to True along with a locked_at timestamp.
    
    Returns the value of the 'cookies' field if successful, or None if no
    unlocked document is available or an error occurs.
    """
    try:
        # Connect to MongoDB using MongoClient with your MONGO_URI.
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["trocu"]
        collection = db["cookiesk"]

        # Build an aggregation pipeline to randomly sample one unlocked document.
        pipeline = [
            {"$match": {"is_locked": False}},
            {"$sample": {"size": 1}}
        ]
        docs = list(collection.aggregate(pipeline))
        if not docs:
            logging.info("No unlocked cookie document available.")
            return None
        
        doc = docs[0]
        cookie_value = doc.get("cookies")
        #logging.info("Retrieved cookie: %s", cookie_value)

        # Lock the document by setting is_locked to True and adding the locked_at timestamp.
        update_result = collection.update_one(
            {"_id": doc["_id"], "is_locked": False},  # Ensure the document is still unlocked.
            {"$set": {"is_locked": True, "locked_at": datetime.utcnow()}}
        )

        if update_result.modified_count:
            logging.info("Cookie document locked successfully.")
        else:
            logging.info("The document was already locked by someone else.")

        return cookie_value

    except Exception as e:
        logging.error("Error retrieving and locking cookie: %s", e)
        return None

    finally:
        client.close()

def retrieve_and_delete_first_chat_entry():
    """
    Connects to the MongoDB Atlas collection 'chat', retrieves the first document (sorted by _id)
    by extracting the 'chattext' field, and then deletes that document.
    
    Returns:
        The value of 'chattext' from the retrieved document, or None if no document is found.
    """
    try:
        client = MongoClient(MONGO_URI,tls=True,tlsAllowInvalidCertificates=True)
        db = client["trocu"]
        collection = db["chat"]

        # Retrieve and delete the earliest inserted document.
        # Sorting with _id (which is an ObjectId) in ascending order typically gives you
        # the oldest (or first) inserted document.
        doc = collection.find_one_and_delete({},sort=[('_id', 1)])
        
        if not doc:
            logging.info("No chat entries found in the collection.")
            return None

        chattext = doc.get("chattext")
        logging.info("Retrieved and deleted chat entry with chattext: %s", chattext)
        return chattext

    except Exception as e:
        logging.error("Error retrieving and deleting chat entry: %s", e)
        return None
    finally:
        client.close()
unlock_expired_documents()
geo_data = requests.get("http://ip-api.com/json/").json()

latitude = geo_data["lat"]
longitude = geo_data["lon"]
timezone_id = geo_data["timezone"]
language_code = geo_data["countryCode"].lower()  # e.g., 'us' -> 'en-US'

with SB(uc=True, test=True,locale=f"{language_code.upper()}") as adads:
    adads.execute_cdp_cmd(
        "Emulation.setGeolocationOverride",
        {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": 100
        }
    )
    adads.execute_cdp_cmd(
        "Emulation.setTimezoneOverride",
        {"timezoneId": timezone_id}
    )
    if True:
        url = "https://www.twitch.tv/brutalles"
        adads.uc_open_with_reconnect(url, 5)
        adads.sleep(20)
        if adads.is_element_present('button:contains("Accept")'):
            adads.uc_click('button:contains("Accept")', reconnect_time=4)
        if True:#adads.is_element_present("#live-channel-stream-information"):
            #adads.uc_click('button:contains("Accept")', reconnect_time=4)
            adads2 = adads.get_new_driver(undetectable=True)
            url1 = "https://kick.com/brutalles"
            adads2.uc_open_with_reconnect(url1, 5)
            adads2.uc_gui_click_captcha()
            adads2.uc_gui_handle_captcha()
            adads2.sleep(10)
            adads.switch_to_driver(adads2)
        if True:
            try:
                cookies = retrieve_and_lock_random_cookie()
                cookiesx = str(cookies)
                if cookies != None:
                    cookie_list = ast.literal_eval(cookiesx.strip()[len("{'cookies':"):-1].strip())
                    for cookie in cookie_list:
                        #print(cookie)
                        adads.add_cookie(cookie)
                    #sb.add_cookies(cookie_list)
                    chatter = 1
                    adads.refresh()
            except Exception as e:
                print(e)
        rnd = random.randint(20,30)
        adads.sleep(rnd)
        if adads.is_element_present('h2:contains("Oops, something went wrong")'):
            adads.clear_cookies()
            adads.refresh()
            chatter = 0
            delete_entry(cookies)
        try:
            if chatter == 1 and adads.is_element_present('button:contains("Follow")'):
                adads.click('button:contains("Follow")')
        except Exception as e:
            print(e)
        while adads.is_element_visible('#injected-channel-player'):
            
            if adads.is_element_present('button:contains("I am 18+")'):
                adads.click('button:contains("I am 18+")')
                #adads.click('button:contains("I am 18+")')
    
            if adads.is_element_present('button:contains("Accept")'):
                adads.click('button:contains("Accept")')
                #adads.click('button:contains("Accept")')
    
            if adads.is_element_present('button:contains("agree")'):
                adads.click('button:contains("agree")')
                #adads.click('button:contains("agree")')
            if chatter == 1:
                try:
                    random_index = random.randint(1, 50)
                    if random_index <=10:
                        try:
                            selector = f"#quick-emotes-holder > div > div:nth-child({random_index})"
                            rnd = random.randint(1,2)
                            adads.sleep(rnd)
                            adads.mouse_click(selector)
                            rnd = random.randint(1,2)
                            adads.sleep(rnd)
                        except Exception as e:
                            print(e)
                    adads.mouse_click("p.editor-paragraph")
                    #adads.hover_and_click("p.editor-paragraph", "p.editor-paragraph")
                    rnd = random.randint(1,5)
                    adads.sleep(rnd)
                    chtmsg = retrieve_and_delete_first_chat_entry()
                    #adads.click("p.editor-paragraph")
                    if chtmsg != None:
                        adads.type("p.editor-paragraph", f"{chtmsg}\n")
                        #adads.gui_write(chtmsg)
                        #adads.press_keys("p.editor-paragraph", "chtmsg" + "\n")
                        #adads.press_keys("\n")#
                        adads.mouse_click("#send-message-button")
                except:
                    print("BAM")
            adads.sleep(100)
