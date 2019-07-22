# -*- coding: utf-8 -*-
"""
Created on Sat May  4 11:34:09 2019

@author: Zero
"""

from bs4 import BeautifulSoup as bs

with open('sign_up_new.html','w') as f:
    soup=bs(open('sign_up.html'))
    f.write(soup.prettify())