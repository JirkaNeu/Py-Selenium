from jne import prinje

try:
  with open("jne.txt", "r", encoding="utf-8") as notes:
    getnotes = []
    for lines in notes:
      getnotes.append(lines.strip("\r\n"))
    notes.close()
    path = getnotes[0]
    path = '/'.join(path.split('\\'))
except:
  path = ""
  try: import ctypes; ctypes.windll.user32.MessageBoxW(0, "check path...", "Python", 1)
  except: print("check path...")

from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import os
import csv
import re
from datetime import datetime, timedelta


import torch
from transformers import pipeline
model = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis")

def get_sentiment(this_input):
    headline_senti = model(this_input)
    senti_score = headline_senti[0]['score']
    headline_senti = headline_senti[0]['label']
    return headline_senti

try:
    today = datetime.now().date()
    yesterday = today - timedelta(days = 1)
    beforeyesterday = today - timedelta(days = 2)
    today = today.strftime("%Y-%m-%d")
    yesterday = yesterday.strftime("%Y-%m-%d")
    beforeyesterday = beforeyesterday.strftime("%Y-%m-%d")

    def clear_string(workstring):
        clear1 = re.compile('<.*?>') #find html-tags
        clear2 = re.compile(r'^\s+') #find spaces bevor 1st word
        clear3 = re.compile(r'\s+$') #find spaces after last word
        clear4 = re.compile(r'\s+') #find consecutive spaces between words
        stringclear = re.sub(clear1, '', workstring)
        stringclear = re.sub(clear2, '', stringclear)
        stringclear = re.sub(clear3, '', stringclear)
        stringclear = re.sub(clear4, ' ', stringclear) #replace by one space
        return stringclear

    def extract_date(rawstamp):
        clearbefore = re.compile(r'^.*?"')
        clearafter = re.compile(r'T.*')
        extracted_date = re.sub(clearbefore, '', rawstamp)
        extracted_date = re.sub(clearafter, '', extracted_date)
        return extracted_date

    PagePath = 'https://www.zeit.de/news/index'

    driver = webdriver.Firefox()
    driver.get(PagePath)

    Page_Result_t = driver.title

    nArticles = len(driver.find_elements(By.XPATH, "/html/body/div[4]/div/main/div/div[2]/article"))
    #nArticles = len(nArticles)
    result_list = []

    def get_Schlagzeile(ArtNr):
        Page_Result10 = driver.find_element(By.XPATH, "/html/body/div[4]/div/main/div/div[2]/article[" + str(ArtNr) + "]/div/div/time")
        Page_Result11 = driver.find_element(By.XPATH, "/html/body/div[4]/div/main/div/div[2]/article[" + str(ArtNr) + "]/div/a/h3/span[1]")
        Page_Result12 = driver.find_element(By.XPATH, "/html/body/div[4]/div/main/div/div[2]/article[" + str(ArtNr) + "]/div/a/h3/span[3]")
        Page_Result13 = driver.find_element(By.XPATH, "/html/body/div[4]/div/main/div/div[2]/article[" + str(ArtNr) + "]/div/div/span")
        Page_Result14 = driver.find_element(By.XPATH, "/html/body/div[4]/div/main/div/div[2]/article[" + str(ArtNr) + "]/div/a")
        #Page_Result14 = driver.find_element(By.CLASS_NAME, "/html/body/div[4]/div/main/div/div[2]/article[" + str(ArtNr) + "]/div/a")
        #
        SZeile101 = Page_Result10.get_attribute('outerHTML')# Timestamp
        DateExtract = extract_date(SZeile101) # extract Date out of Timestamp
        SZeile102 = Page_Result10.get_attribute('innerHTML')# Zeitangabe
        SZeile11 = Page_Result11.get_attribute('innerHTML')# Kategorie
        SZeile11 = clear_string(SZeile11) # remove unwanted stuff
        SZeile12 = Page_Result12.get_attribute('innerHTML')# Schlagzeile
        SZeile13 = Page_Result13.get_attribute('innerHTML')# Quelle/Ort
        SZeile14 = Page_Result14.get_attribute('href')# Hyperlink
        SZ_senti = get_sentiment(SZeile12)# get sentiment of headline
        #
        global abbruch
        if DateExtract == today or DateExtract == yesterday or DateExtract == beforeyesterday:
            result_list.append([ArtNr, SZeile101, DateExtract, SZeile102, SZeile11, SZeile12, SZeile13, SZeile14, SZ_senti])
        else:
            abbruch = True

    abbruch = False
    iz = 1
    while iz <= nArticles:
        get_Schlagzeile(iz)
        #print(iz)
        if iz == 850:
            break
        if abbruch == True:
            break
        iz += 1

    time.sleep(1)
    driver.close()
    driver.quit()

    print("nArticles: " + str(nArticles))
    print("today: " + str(today))
    print("yesterday: " + str(yesterday))
    print("beforeyesterday: " + str(beforeyesterday))
except:
    print("some error occurred")

# --------------- write file ---------------#
def fill_file(file_name):
    with open(file_name, 'a', newline='') as file:
        fill_file = csv.writer(file)
        fill_file.writerows(result_list)
    return None

def results_to_file():
    file_name = "Page_Results.csv"
    if not os.path.exists(file_name):
        head_row = [['Nr.', 'Timestamp', 'Datum', 'Zeitangabe', 'Kategorie', 'Schlagzeile', 'Quelle/Ort', 'Link', 'Sentiment']]
        with open(file_name, 'w', newline='') as file:
            preparefile = csv.writer(file)
            preparefile.writerows(head_row)
        fill_file(file_name)
    else:
        fill_file(file_name)
    return None
results_to_file()


# --------------- simple bar chart ---------------#
import pandas as pd

plot_values = []
for i in range(len(result_list)):
    plot_values.append(result_list[i][8])

jne_results = pd.DataFrame()
jne_results = jne_results.assign(Sentiments = plot_values)
count_values = jne_results['Sentiments'].value_counts()
jne_output = pd.DataFrame({'Sentiments': count_values.index, 'counts': count_values.values})

#https://pythonspot.com/matplotlib-bar-chart/
import matplotlib.pyplot as plt
fig, ax = plt.subplots()

plot_results = jne_output

cats = plot_results["Sentiments"].apply(lambda x: str(x)[:10])
vals = plot_results["counts"]

ax.bar(cats, vals)
ax.set_title('Sentiments of headlines')
ax.set_xlabel('Sentiments')
ax.set_ylabel('Frequency')
#plt.xticks(rotation=45, ha='right')
plt.xticks(rotation=35, ha='right')

plt.show()


