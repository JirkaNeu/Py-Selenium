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

