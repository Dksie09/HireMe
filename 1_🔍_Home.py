import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import time
from io import StringIO
# import io,random
from pyresparser import ResumeParser
import re
import pickle
from ftfy import fix_text
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df_new = movie_list = pickle.load(open("df_new.pkl", "rb"))

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def ngrams(string, n=3):
    string = fix_text(string) # fix text
    string = string.encode("ascii", errors="ignore").decode() #remove non ascii chars
    string = string.lower()
    chars_to_remove = [")","(",".","|","[","]","{","}","'"]
    rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
    string = re.sub(rx, '', string)
    string = string.replace('&', 'and')
    string = string.replace(',', ' ')
    string = string.replace('-', ' ')
    string = string.title() # normalise case - capital at start of each word
    string = re.sub(' +',' ',string).strip() # get rid of multiple spaces and replace with a single
    string = ' '+ string +' ' # pad names for ngrams...
    string = re.sub(r'[,-./]|\sBD',r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams]

def pie_chart(ans):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = ans['Company Name']+'\n('+ans['Job Title']+')'
    sizes = ans['match']
    # explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
             startangle=90, textprops={'color': "w"})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    fig1.patch.set_facecolor('none')
    st.pyplot(fig1)


def recommend(skills):
    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams, lowercase=False)
    tfidf = vectorizer.fit_transform(skills)
    nbrs = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(tfidf)
    test = (df_new['Tags'].values.astype('U'))
    def getNearestN(query):
        queryTFIDF_ = vectorizer.transform(query)
        distances, indices = nbrs.kneighbors(queryTFIDF_)
        return distances, indices
    
    distances, indices = getNearestN(test)
    test = list(test) 
    matches = []
    for i,j in enumerate(indices):
        dist=round(distances[i][0],2)
    
        temp = [dist]
        matches.append(temp)
    
    matches = pd.DataFrame(matches, columns=['Match confidence'])
    df_new['match']=matches['Match confidence']
    df1=df_new.sort_values('match')
    ans1=df1.sort_values(by='match', ascending=False)
    ans=df1.sort_values(by='match', ascending=False).head(6)
    
    # st.caption('Some jobs recommended for you are:')
    # st.write(":heavy_minus_sign:" * 32)
    st.write(" ")
    pie_chart(ans1.head(10))
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write(ans[['Company Name','Job Title','Location','Skills Required']])   
    
    #----------



# st.title('HireMe')
#add picture
image = Image.open('hireme_logo_cropped.png')
st.image(image)
# st.caption('HireMe')
st.caption("Welcome to HireME, \n\n*the revolutionary job search platform that helps you find your dream job without the hassle of endlessly browsing through multiple job websites.* ")

# uploaded_file = None
# if st.button('Get Started'): 
st.info('Upload your resume to get started :)', icon="ℹ️")
time.sleep(0.5)
uploaded_file = st.file_uploader("Drop your resume here", type=['pdf'])
new_data = None

if uploaded_file is not None:
    st.spinner(text='Uploading your resume...')
    # time.sleep(1.5)
    
    save_path = './uploaded_resume'+uploaded_file.name
    with open(save_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    data = ResumeParser(save_path).get_extracted_data()
    if data['skills']:
        st.success('Successfully uploaded resume', icon="✅")
        time.sleep(1)
        new_data = data['skills']
        new_data = [' '.join(new_data)]
        new_data = [s.lower() for s in new_data]
        new_data = [''.join(c for c in s if c.isalnum() or c==' ') for s in new_data]
        resume_text = pdf_reader(save_path)

    
        print(new_data)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            st.header('Hello, '+data['name']+'!')
        except:
            st.header('Hello!')
        components.html("""<hr style="height:10px;border:none;color:#333;background: linear-gradient(to right, purple, blue);margin-bottom: 0;" /> """)
        recommend(new_data)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button('ReUpload',type="primary"):
            st.experimental_rerun()
            # st.write('Analyzing your resume...')
            # time.sleep(1)
            st.success('Resume analysis complete!', icon="✅")
            st.write(resume_text)
    else:
        #write error message
        st.error('No information found in your resume', icon="🚨")
else:
    time.sleep(0.5)
    st.warning('*Attention!* If you don\'t have a resume, head over to the "Create Resume" section of our website.', icon="⚠️")





# st.write('Your skills are: ', new_data)
    

