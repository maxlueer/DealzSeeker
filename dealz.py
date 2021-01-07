#!/usr/bin/python
# coding=utf-8

import datetime
import json
import os
import re
import requests
import sys
import telebot
import threading
import time
import traceback

from bs4 import BeautifulSoup as bs
from contextlib import suppress
from colorama import init, Fore, Back, Style
from emoji import emojize
from threading import Thread

# Emoji definitions
wave = emojize(":wave:", use_aliases=True)
hot = emojize(":fire:", use_aliases=True)
free = emojize(":free:", use_aliases=True)
wish = emojize(":star:", use_aliases=True)

# Basic stuff
os.chdir(os.path.dirname(os.path.realpath(__file__)))
init(autoreset=True) # Colorama
header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36 OPR/55.0.2994.61"}

# Get settings from file
def get_settings():
    global debug_mode; global short_url; global telegram
    global sleep_time; global tg_token; global tg_token_priority
    global tg_cid; global tg_cid2

    debug_mode = 0
    short_url = 0
    telegram = 0

    settings = {}
    exec(open("./settings.txt").read(), None, settings)
    if settings["debug_mode"]:
        debug_mode = 1
    if settings["telegram"]:
        telegram = 1
    sleep_time = settings["sleep_time"]
    tg_token = settings["tg_token"]
    tg_token_priority = 0
    tg_cid = settings["tg_cid"]
    tg_cid2 = settings["tg_cid2"]

get_settings()

# Debug mode
def debug(text):	
    if debug_mode:
    	print(Fore.YELLOW + "DEBUG: " + text)
    return 0

# Get already found deals from file
def get_found():
    global found_deals; global found_deals2; global found_deals_idealo; global found_deals_idealo2
    found_deals = [line.rstrip("\n") for line in open ("./found_{}.txt".format(tg_cid))]
    found_deals_idealo = [line.rstrip("\n") for line in open ("./found_idealo_{}.txt".format(tg_cid))]
    found_deals2 = [line.rstrip("\n") for line in open ("./found_{}.txt".format(tg_cid2))]
    found_deals_idealo2 = [line.rstrip("\n") for line in open ("./found_idealo_{}.txt".format(tg_cid2))]

# Get wanted articles from file
def get_wanted():
    global wanted_articles; global wanted_articles2; global wanted_articles_idealo; global wanted_articles_idealo_2
    wanted_articles = [line.rstrip("\n") for line in open ("./wanted_{}.txt".format(tg_cid))]
    wanted_articles_idealo = [line.rstrip("\n") for line in open ("./wanted_idealo_{}.txt".format(tg_cid))]
    wanted_articles2 = [line.rstrip("\n") for line in open ("./wanted_{}.txt".format(tg_cid2))]
    wanted_articles_idealo_2 = [line.rstrip("\n") for line in open ("./wanted_idealo_{}.txt".format(tg_cid2))]

# Telegram bot
bot = telebot.TeleBot(tg_token)

@bot.message_handler(commands=["hello"])
def hello(msg):
    cid = msg.chat.id
    bot.send_message(cid, "Hi! " + wave + " Ich bin noch da, keine Sorge.")

@bot.message_handler(commands=["addMyDealz"])
def add_item(msg):
    cid = msg.chat.id
    messageReplaced = msg.text.replace("/addMyDealz ", "")
    if len(messageReplaced) <= 0:
        bot.send_message(cid, "Falsche Eingabe! i.e. /addMyDealz samsung evo 960")
        return

    with open("./wanted_{}.txt".format(cid), "a") as f:
        f.write(messageReplaced + "\n")
    bot.send_message(cid, "Schlagwort wurde der Liste hinzugefügt: " + messageReplaced)
    get_wanted()

@bot.message_handler(commands=["addIdealo"])
def add_item(msg):
    cid = msg.chat.id
    messageReplaced = msg.text.replace("/addIdealo ", "")
    semikolonIndex = messageReplaced.find(";")
    if semikolonIndex <= 0:
        bot.send_message(cid, "Falsche Eingabe! i.e. /addIdealo https://www.idealo.de/preisvergleich/ProductCategory/16073F101483660.html;200")
        return
    try:
        price = int(messageReplaced[semikolonIndex+1:])
    except:
        bot.send_message(cid, "Falsche Eingabe! (nach Semikolon muss Integer stehen) i.e. /addIdealo https://www.idealo.de/preisvergleich/ProductCategory/16073F101483660.html;200")
        return

    message = messageReplaced[:semikolonIndex]
    with open("./wanted_idealo_{}.txt".format(cid), "a") as f:
        f.write(message + ";" + str(price) + "\n")
    bot.send_message(cid, "Link wurde der Liste hinzugefügt. Preisalarm fuer Idealo ab: " + str(price) + " EUR")
    get_wanted()

@bot.message_handler(commands=["removeMyDealz"])
def remove_item(msg):
    cid = msg.chat.id
    with open("./wanted_{}.txt".format(cid), "r") as list:
        lines = list.readlines()
    with open("./wanted_{}.txt".format(cid), "w") as remove:
        for line in lines:
            if line.lower() != (msg.text.replace("/removeMyDealz ", "") + "\n").lower():
                remove.write(line)
    bot.send_message(cid, "Schlagwort \""+ msg.text.replace("/removeMyDealz ", "") +"\" wurde von der Liste entfernt.")
    get_wanted()

@bot.message_handler(commands=["removeIdealo"])
def remove_item(msg):
    cid = msg.chat.id
    with open("./wanted_idealo_{}.txt".format(cid), "r") as list:
        lines = list.readlines()
    with open("./wanted_idealo_{}.txt".format(cid), "w") as remove:
        for line in lines:
            if line.lower() != (msg.text.replace("/removeIdealo ", "") + "\n").lower():
                remove.write(line)
    bot.send_message(cid, "Link wurde von der Liste entfernt.")
    get_wanted()

@bot.message_handler(commands=["reset"])
def reset_found(msg):
    cid = msg.chat.id
    open("./found_{}.txt".format(cid), "w").close()
    open("./found_idealo_{}.txt".format(cid), "w").close()
    bot.send_message(cid, "Liste der gefundenen Deals wurde geleert.")
    get_found()

@bot.message_handler(commands=["list"])
def list_items(msg):
    cid = msg.chat.id
    with open("./wanted_{}.txt".format(cid), "r") as list:
        lines = list.readlines()
    bot.send_message(cid, "[MyDealz] Suche nach Deals für: " + str(lines).replace("[", "").replace("]", "")) # fix \n

    with open("./wanted_idealo_{}.txt".format(cid), "r") as list:
        lines = list.readlines()
    bot.send_message(cid, "[MyDealz] Suche nach Deals für: " + str(lines).replace("[", "").replace("]", "")) # fix \n

def telegram_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            debug(traceback.format_exc())
            time.sleep(5)

# seeking routines
def mydealz_search(tg_cid, found_deals, articles, wanted_articles):
    for wanted_item_full in wanted_articles:
        wanted_item = wanted_item_full[:wanted_item_full.find(";")]
        deals = articles.find_all("a", string=re.compile("(?i).*("+wanted_item+").*"), class_="cept-tt thread-link linkPlain thread-title--list")
        for thread in deals:
            dealid = articles.attrs["id"]
            if dealid in found_deals:
                debug("Deal already found " + dealid)
                continue
            title = thread.string.strip()
            proc_link = thread.get("href")

            print("[MYDEALZ] %s: %s" % (re.sub(r"[^\x00-\x7F]+"," ", title), proc_link))
            if telegram:
                bot.send_message(tg_cid, wish + " [MYDEALZ] %s: %s" % (title, proc_link), disable_web_page_preview=True)
            with open("./found_{}.txt".format(tg_cid), "a") as found:
                found.write(dealid + "\n")
            get_found()
            time.sleep(4)

def mydealz():
    print("MyDealz")
    site = requests.get("https://www.mydealz.de/new?page=1", headers=header, timeout=20)
    soup = bs(site.content, "lxml")
    debug("Request completed")

    listings = soup.find_all("article", {"id":re.compile("thread_.*")})
    if listings is None:
        print("Keine Listings gefunden. Seite geändert?")

    for articles in listings:
        mydealz_search(tg_cid, found_deals, articles, wanted_articles)
        if tg_cid2 != 0:
            mydealz_search(tg_cid2, found_deals2, articles, wanted_articles2)

def idealo_search(tg_cid, found_deals, wanted_articles):
    for wanted_item_full in wanted_articles:
        wanted_item_url = wanted_item_full[:wanted_item_full.find(";")]
        wanted_item_price = int(wanted_item_full[wanted_item_full.find(";") + 1:])

        site = requests.get(wanted_item_url, headers=header, timeout=20)
        soup = bs(site.content, "lxml")
        listings = soup.find_all("div", {"class":"offerList-item"})
        print(wanted_item_url)
        for listing in listings:
            try:
                listing_price_div = str(listing.find_all("div", {"class":"offerList-item-priceMin"})[0])
                listing_price = re.findall('[0-9]*\.*[0-9][0-9]*,[0-9][0-9]', listing_price_div)
                listing_price = listing_price[0].replace(".","")
                listing_price = float(listing_price.replace(",","."))

                # check if price is better than wanted
                if wanted_item_price < listing_price:
                    continue
                
                listingID = int(re.findall('[0-9]{7,10}', listing.get('data-gtm-payload'))[0])

                idAndPrice = str(listingID) + ";" + str(listing_price)

                if idAndPrice in found_deals:
                    debug("Deal already found: " + listingID)
                    continue
                
                listingName = re.findall("[A-Za-z0-9].*$", listing.find_all("div", {"class":"offerList-item-description-title"})[0].text)[0]
                
                listingLink = "https://www.idealo.de" + str(listing.find_all("a", {"class":"offerList-itemWrapper"})[0].get('href'))

                print("[IDEALO Preisalarm] %s ab %s EUR: %s" % (listingName, str(listing_price), listingLink))
                if telegram:
                    bot.send_message(tg_cid, wish + " [IDEALO Preisalarm] %s ab %s EUR: %s" % (listingName, str(listing_price), listingLink), disable_web_page_preview=True)
                with open("./found_idealo_{}.txt".format(tg_cid), "a") as found:
                    found.write(idAndPrice + "\n")
                get_found()
            except:
                debug("Idealo: Search Failed")
            time.sleep(1)

def idealo():
    print("Idealo")
    idealo_search(tg_cid, found_deals_idealo, wanted_articles_idealo)
    if tg_cid2 != 0:
        idealo_search(tg_cid2, found_deals_idealo2, wanted_articles_idealo2)

# seeker
def main_seeker():
    while True:
        # Wanted scraper
        try:
            debug("Seeking for wanted items")

            mydealz()

            idealo()

            debug("Seeking for wanted items complete")
        except:
            debug(traceback.format_exc())
            time.sleep(60)
        
        debug("Now sleeping until next cycle")
        time.sleep(sleep_time)

if __name__=="__main__":
    # Check for required files
    with suppress(Exception):
        open("./wanted_{}.txt".format(tg_cid), "x")
    with suppress(Exception):
        open("./found_{}.txt".format(tg_cid), "x")
    with suppress(Exception):
        open("./wanted_{}.txt".format(tg_cid2), "x")
    with suppress(Exception):
        open("./found_{}.txt".format(tg_cid2), "x")
    with suppress(Exception):
        open("./wanted_idealo_{}.txt".format(tg_cid), "x")
    with suppress(Exception):
        open("./found_idealo_{}.txt".format(tg_cid), "x")
    with suppress(Exception):
        open("./wanted_idealo_{}.txt".format(tg_cid2), "x")
    with suppress(Exception):
        open("./found_idealo_{}.txt".format(tg_cid2), "x")

    # Initial fetch
    get_wanted()
    get_found()

    Thread(target = telegram_bot).start()
    Thread(target = main_seeker).start()
