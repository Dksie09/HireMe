import streamlit as st
from PIL import Image
from pyresparser import ResumeParser
import re
import pickle
import pandas as pd
import numpy as np

# def recommend(data):



st.title('HireMe')
#add picture
# image = Image.open('hireme_logo.png')
# st.image(image)

uploaded_file = st.file_uploader("Drop your resume here", type=['pdf'])
if uploaded_file is not None:
    
    data = ResumeParser('Resume.pdf').get_extracted_data()
    new_data = data['skills']
    new_data = ' '.join(new_data)
    # remove any characters that are not alphanumeric or spaces
    new_data = re.sub('[^\w\s]', '', new_data)
    #to lower case
    new_data = new_data.lower()
    st.write(new_data)
    #new data se kaam krna ab

df_new = movie_list = pickle.load(open("df_new.pkl", "rb"))

st.write(df_new)

