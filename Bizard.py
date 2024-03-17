import streamlit as st
import sqlite3
import re
from PIL import Image
import easyocr
import pandas as pd
import numpy as np

def image_to_text(path):

     input_img= Image.open(path)
     #converting image to array formet
     image_arr= np.array(input_img)

     reader= easyocr.Reader(['en'])
     text= reader.readtext(image_arr,detail= 0)
     return text,input_img

def extracted_text(texts):
    extrd_dict = {"NAME":[],"DESIGNATION":[],"COMPANY_NAME":[],"CONTACT":[],"EMAIL":[],
                  "WEBSITE":[],"ADDRESS":[],"CITY":[],"STATE":[],"PINCODE":[]}
    extrd_dict["NAME"].append(texts[0])
    extrd_dict["DESIGNATION"].append(texts[1])

    for i in range(2,len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
            extrd_dict["CONTACT"].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:
            small =texts[i].lower()
            extrd_dict["EMAIL"].append(small)

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            small = texts[i].lower()
            extrd_dict["WEBSITE"].append(small)

        elif "Tamil Nadu" in texts[i]  or "TamilNadu" in texts[i] or texts[i].isdigit():
            
            extrd_dict["PINCODE"].append(texts[i].split(" ")[1].strip())
            extrd_dict["STATE"].append(texts[i].split(" ")[0].strip())

        elif re.match(r'^[A-Za-z]',texts[i]):
            extrd_dict["COMPANY_NAME"].append(texts[i])
        
        else:                
                city = re.sub(r'[,;]', '',texts[i].split(',')[1])
                address = re.sub(r'[,;]', '',texts[i].split(',')[0])
                extrd_dict["CITY"].append(city)
                extrd_dict["ADDRESS"].append(address)


    for key,value in extrd_dict.items():
        if len(value)>0:
            concadenate = ' '.join(value)
            extrd_dict[key] = [concadenate]
        else:
            value = 'NA'
            extrd_dict[key] = [value]

    return extrd_dict
def fetch_data():
    conn = sqlite3.connect('bizcardx.db')
    cursor = conn.cursor()
    query= "select * from bizcard_details"
    cursor.execute(query)
    table = cursor.fetchall()
    conn.commit()

    df6= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                                "EMAIL","WEBSITE","ADDRESS","CITY","STATE","PINCODE","IMAGE"])

    return df6