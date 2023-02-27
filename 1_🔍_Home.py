import streamlit as st
import streamlit.components.v1 as components
import urllib.request
from PIL import Image
import time
from io import StringIO
from pyresparser import ResumeParser
import re
import pickle
from ftfy import fix_text
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import string
from nltk.corpus import stopwords
# from rapidfuzz import fuzz
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.neighbors import NearestNeighbors
# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df_new = movie_list = pickle.load(open("df_new.pkl", "rb"))

#to get pdf text
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

#procceed resume text
def remove_html(text):
    html_tags = re.compile('<.*?>')
    return re.sub(html_tags, '', text)
def remove_url(text):
    url = re.compile(r'https?://\S+|www\.\S+')
    #remove gmail id
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)
    return re.sub(url, '', text)
def convert_to_pp(text):
    text = text.replace('+', 'p')
    return text
def remove_punct(text):
    table=str.maketrans('','',string.punctuation)
    return text.translate(table)
def remove_n(text):
    n = re.compile(r'\n')
    return re.sub(n, ' ', text)
def remove_extra_space(text):
    return re.sub(' +', ' ', text)
def remove_numbers(text):
    number = re.compile(r'\d+')
    return re.sub(number, '', text)
def remove_words_starting_with_prefix(text, prefix):
    words = text.split()
    filtered_words = [word for word in words if not word.startswith(prefix)]
    return ' '.join(filtered_words)
def remove_bullet_points(text):
    text = text.replace('●', '')
    text = text.replace('○', '')
    text = text.replace('•', '')
    return text
def remove_dash(text):
    text = text.replace('-', '')
    return text
def remove_stopwords(text):
    new_text=[]
    for word in text.split():
        if word not in stopwords.words('english'):
            new_text.append(word)
    return ' '.join(new_text)

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


def recommend3(skills, df_new):
    df_new = df_new.reset_index(drop=True)
    score = []
    count=0
    # st.write(df_new['Tags'][1])
    for i in range(len(df_new)):
        # word_count=0
        for j in skills.split():
            for k in df_new['Tags'][i].split():
                # word_count+=1
                # st.write(k)
                if j==k:
                    count=count+1
                    break
        score.append(count)
        count=0
    # st.write(score)
    max_score = max(score)
    if max_score > 0:
        score = [round((s/max_score)*10, 2) for s in score]
    else:
        score = [0] * len(df_new)
    df_new["Score"] = score
    ans = df_new.sort_values(by=['Score'], ascending=False)
    # st.write(ans.head(10))
    tab2, tab1 = st.tabs(["Details", "List"])
    with tab1:
        st.dataframe(ans[['Company Name','Job Title','Location','Skills Required','Score']].head(10))   
    with tab2:
        for i in range(6):
            with st.container():
                cola, colb = st.columns(2)
                with cola:
                    # st.header(ans.head()['Company Name'].values[0])
                    url = ans['Logo'].values[i]
                    filename = 'logo.png'
                    urllib.request.urlretrieve(url, filename)

            # Open the downloaded image and display it using st.image()
                    image = Image.open(filename)
                    
                    st.subheader(ans['Job Title'].values[i])
                    st.image(image)
                    
                    try:
                        # ans.head()['Skills Required'].values[0].replace("  " , " ")
                        st.button(ans['Skills Required'].values[i], disabled=True)
                    except:
                        pass
                    
                with colb:
                    # st.write("*About*")
                    st.header(ans['Company Name'].values[i])
                    st.write(ans['About Company'].values[i].split('\n')[0])
                    try:
                        st.button(ans['Location'].values[i])
                    except:
                        pass
                    st.markdown("<br><br>", unsafe_allow_html=True)

# def recommend2(skills, df_new):
#     # df_new['match'] = df_new['Tags'].apply(lambda x: fuzz.token_set_ratio(x, skills))

#     # # Sort the DataFrame in descending order with respect to the 'match' column
#     # df_new = df_new.sort_values(by='match',
#     #  ascending=False)

#     # # Print the resulting DataFrame
#     # st.write(df_new.head(10))
#     # Compute the cosine similarity between the 'tags' column and the user input
#     tfidf = TfidfVectorizer()
#     corpus = df_new['Tags'].tolist() + [skills]
#     tfidf_matrix = tfidf.fit_transform(corpus)
#     cosine_similarities = cosine_similarity(tfidf_matrix[:-1], tfidf_matrix[-1])

#     # Add the 'match' column to the DataFrame
#     df_new['match'] = cosine_similarities

#     # Sort the DataFrame in descending order with respect to the 'match' column
#     df = df_new.sort_values(by='match', ascending=False)
#     st.write(df.head(10))

# def recommend(skills):
#     st.write("Skills: ", skills)
#     # st.write(df_new['Tags'][0])
#     # print(df_new.head())
#     vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams, lowercase=False)
#     tfidf = vectorizer.fit_transform(skills)
#     nbrs = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(tfidf)
#     test = (df_new['Tags'].values.astype('U'))
#     def getNearestN(query):
#         queryTFIDF_ = vectorizer.transform(query)
#         distances, indices = nbrs.kneighbors(queryTFIDF_)
#         return distances, indices
    
#     distances, indices = getNearestN(test)
#     test = list(test) 
#     matches = []
#     for i,j in enumerate(indices):
#         dist=round(distances[i][0],2)
    
#         temp = [dist]
#         matches.append(temp)
    
#     matches = pd.DataFrame(matches, columns=['Match confidence'])
#     df_new['match']=matches['Match confidence']
#     df1=df_new.sort_values('match')
#     ans1=df1.sort_values(by='match', ascending=False)
#     ans=df1.sort_values(by='match', ascending=False).head(10)
#     st.write(ans.head(10))
#     tab2, tab1 = st.tabs(["Details", "List"])
#     with tab1:
#         st.dataframe(ans[['Company Name','Job Title','Location','Skills Required','match']])   
#     with tab2:
#         for i in range(5):
#             with st.container():
#                 cola, colb = st.columns(2)
#                 with cola:
#                     # st.header(ans.head()['Company Name'].values[0])
#                     url = ans.head()['Logo'].values[i]
#                     filename = 'logo.png'
#                     urllib.request.urlretrieve(url, filename)

#             # Open the downloaded image and display it using st.image()
#                     image = Image.open(filename)
                    
#                     st.subheader(ans.head()['Job Title'].values[i])
#                     st.image(image)
                    
#                     try:
#                         # ans.head()['Skills Required'].values[0].replace("  " , " ")
#                         st.button(ans.head()['Skills Required'].values[i], disabled=True)
#                     except:
#                         pass
                    
#                 with colb:
#                     # st.write("*About*")
#                     st.header(ans.head()['Company Name'].values[i])
#                     st.write(ans.head()['About Company'].values[i].split('\n')[0])
#                     try:
#                         st.button(ans.head()['Location'].values[i], disabled=True, type="primary")
#                     except:
#                         pass
#                     st.markdown("<br><br>", unsafe_allow_html=True)
   

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
    
    save_path = './uploaded_resume/'+uploaded_file.name
    with open(save_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    resume_text = pdf_reader(save_path)
    if resume_text:
        st.success('Successfully uploaded resume', icon="✅")
        # st.spinner(text='Analysing your resume...')
        resume_text = resume_text.lower()
        resume_text = remove_html(resume_text)
        resume_text = remove_url(resume_text)
        resume_text = convert_to_pp(resume_text)
        resume_text = remove_punct(resume_text)
        resume_text = remove_n(resume_text)
        resume_text = remove_extra_space(resume_text)
        resume_text = remove_numbers(resume_text)
        resume_text = remove_words_starting_with_prefix(resume_text, '\\')
        resume_text = remove_bullet_points(resume_text)
        resume_text = remove_dash(resume_text)
        resume_text = remove_stopwords(resume_text)
        data = ResumeParser(save_path).get_extracted_data()
    # if data['skills']:
    #     st.success('Successfully uploaded resume', icon="✅")
    #     time.sleep(1)
    #     new_data = data['skills']
    #     new_data = [' '.join(new_data)]
    #     new_data = [s.lower() for s in new_data]
    #     new_data = [''.join(c for c in s if c.isalnum() or c==' ') for s in new_data]
        # resume_text = pdf_reader(save_path)

    
        print(resume_text)
        # resume_text = [resume_text]
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            st.header('Hello, '+data['name']+'!')
        except:
            st.header('Hello!')
        components.html("""<hr style="height:10px;border:none;color:#333;background: linear-gradient(to right, purple, blue);margin-bottom: 0;" /> """)
        with st.spinner(text='Fetching jobs for you...'):
            # st.write(df_new.columns)
            recommend3(resume_text, df_new)
            # st.write(resume_text)
            st.markdown("<br>", unsafe_allow_html=True)
        
    else:
        #write error message
        st.error('No information found in your resume', icon="🚨")
else:
    time.sleep(0.5)
    st.warning('*Attention!* If you don\'t have a resume, head over to the "Create Resume" section of our website.', icon="⚠️")



button = """
<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="dakshiegoeq" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
"""

components.html(button, height=70, width=220)

st.markdown(
"""
<style>
iframe[width="220"] {
position: fixed;
bottom: 60px;
right: 40px;
}
</style>
""",
unsafe_allow_html=True,
)

# st.write('Your skills are: ', new_data)
    

