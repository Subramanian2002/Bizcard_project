import streamlit as st
import sqlite3
from PIL import Image
import easyocr
import re
import Bizard as b
import numpy as np
from streamlit_option_menu import option_menu
import pandas as pd
import io

def main():
    st.set_page_config(layout= "wide")
    st.title("Business Card Reader App")
    with st.sidebar:
       select= option_menu("Main Menu",["Home", "Upload","View Data","Update Data","Delete"])

    if select == "Home":
        st.subheader("Home")
        st.write("Welcome to the Business Card Reader App!")
        st.write("Choose an option from the sidebar to get started.")

    elif select == "Upload":

        img= st.file_uploader("Upload the Image", type= ["png", "jpg", "jpeg"], label_visibility= "hidden")

        if img is not None:
            st.image(img,width= 300)
            text_image,input_img= b.image_to_text(img)
            text_dict= b.extracted_text(text_image)
            if text_dict:
                 st.success("TEXT IS EXTRACTED SUCCESSFULLY")
            df= pd.DataFrame(text_dict)
            #Converting Image to Bytes
            Image_bytes= io.BytesIO()
            input_img.save(Image_bytes,format= "PNG")
            image_data= Image_bytes.getvalue()
            #Creating dictionary
            data= {"Image":[image_data]}
            df_1= pd.DataFrame(data)
            concat_df= pd.concat([df,df_1],axis=1)
            st.write(concat_df)
            button3= st.button("Save",use_container_width= True)

            if button3:
                conn = sqlite3.connect('bizcardx.db')
                table_name = 'bizcard_details'
                columns = concat_df.columns.tolist()
                # Define the table creation query
                create_table_query = '''
                CREATE TABLE IF NOT EXISTS {} (
                    NAME varchar(225),
                    DESIGNATION varchar(225),
                    COMPANY_NAME varchar(225),
                    CONTACT varchar(225),
                    EMAIL text,
                    WEBSITE text,
                    ADDRESS text,
                    CITY text,
                    STATE text,
                    PINCODE varchar(225),
                    Image text
                )'''.format(table_name)
                conn.execute(create_table_query)
                conn.commit()
                for index, row in concat_df.iterrows():
                    insert_query = '''
                            INSERT INTO {} ({})
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    '''.format(table_name, ', '.join(columns))
                    values= (row['NAME'], row['DESIGNATION'], row['COMPANY_NAME'], row['CONTACT'],
                            row['EMAIL'], row['WEBSITE'], row['ADDRESS'],row['CITY'],row['STATE'],row['PINCODE'],row["Image"])
                    # Execute the insert query
                    conn.execute(insert_query,values)
                    # Commit the changes
                    conn.commit()
    
    
    elif select == "View Data":
        data = b.fetch_data()
        if len(data) > 0:
            st.dataframe(data)
        else:
            st.write("No data available in the database.")
    
    
    elif select == "Update Data":
        conn = sqlite3.connect('bizcardx.db')
        cursor = conn.cursor()
        query= "select * from bizcard_details"
        cursor.execute(query)
        table = cursor.fetchall()
        conn.commit()
        if table:
            df3= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                            "EMAIL","WEBSITE","ADDRESS","CITY","STATE","PINCODE","IMAGE"])
            st.dataframe(df3)
            col1,col2= st.columns(2)
            with col1:
               select_name = st.selectbox("Select the Name",df3["NAME"])
               df4 = df3[df3["NAME"]==select_name]
            st.write("")
            col1,col2= st.columns(2)
            with col1:
                modify_name= st.text_input("Name", df4["NAME"].unique()[0])
                modify_desig= st.text_input("Designation", df4["DESIGNATION"].unique()[0])
                modify_company= st.text_input("Company_Name", df4["COMPANY_NAME"].unique()[0])
                modify_contact= st.text_input("Contact", df4["CONTACT"].unique()[0])
                modify_email= st.text_input("Email", df4["EMAIL"].unique()[0])
                modify_web= st.text_input("Website", df4["WEBSITE"].unique()[0])
            with col2:
                modify_address= st.text_input("Address", df4["ADDRESS"].unique()[0])
                modify_city= st.text_input("City", df4["CITY"].unique()[0])
                modify_state= st.text_input("State", df4["STATE"].unique()[0])
                modify_pincode= st.text_input("Pincode", df4["PINCODE"].unique()[0])
            col1,col2= st.columns(2)
            
            button3= st.button("Modify",use_container_width= True)
            if button3:
                conn = sqlite3.connect('bizcardx.db')
                cursor = conn.cursor()
                cursor.execute('''UPDATE bizcard_details
                            SET NAME=?, DESIGNATION=?, COMPANY_NAME=?, CONTACT=?, EMAIL=?, WEBSITE=?, ADDRESS=?, CITY=?, STATE=?, PINCODE=?
                            WHERE NAME=?''',
                            (modify_name, modify_desig, modify_company, modify_contact, modify_email, modify_web, modify_address, modify_city, modify_state, modify_pincode, select_name))
                conn.commit()
                
                query= "select * from bizcard_details"
                cursor.execute(query)
                table = cursor.fetchall()
                conn.commit()
                df6= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                                        "EMAIL","WEBSITE","ADDRESS","CITY","STATE","PINCODE","IMAGE"])
                st.dataframe(df6)
                st.success("MODIFIED SUCCESSFULLY")
        else:
            st.write("No data available in the database.")         
    elif select == "Delete":

        conn = sqlite3.connect('bizcardx.db')
        cursor= conn.cursor()

        col1,col2= st.columns(2)
        with col1:
            cursor.execute("SELECT NAME FROM bizcard_details")
            conn.commit()
            table1= cursor.fetchall()

            names=[]

            for i in table1:
               names.append(i[0])

            name_select= st.selectbox("Select the Name",options= names)

        with col2:
            cursor.execute(f"SELECT DESIGNATION FROM bizcard_details WHERE NAME ='{name_select}'")
            conn.commit()
            table2= cursor.fetchall()

            designations= []

            for j in table2:
                designations.append(j[0])

            designation_select= st.selectbox("Select the Designation", options= designations)

        if name_select and designation_select:
            col1,col2,col3= st.columns(3)

            with col1:
               st.write(f"Selected Name : {name_select}")
               st.write("")
               st.write("")

            st.write(f"Selected Designation : {designation_select}")

            with col2:
               st.write("")
               st.write("")
               st.write("")
               st.write("")
            remove= st.button("Delete",use_container_width= True)

            if remove:
                conn.execute(f"DELETE FROM bizcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
                conn.commit()

                st.warning("DELETED")
        
main()        