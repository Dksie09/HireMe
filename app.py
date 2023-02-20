import streamlit as st
from PIL import Image
from pyresparser import ResumeParser
import re
import pickle
from ftfy import fix_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df_new = movie_list = pickle.load(open("df_new.pkl", "rb"))

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
    ans=df1.sort_values(by='match', ascending=False).head(5)
    st.write(ans)   
    print(ans)
    #----------
    names = ans['Company Name']+'\n('+ans['Job Title']+')'
    index = ans['match']
    x=plt.pie(index, labels=names, autopct = '%1.1f%%')
    plt.title('Top 5 Jobs')
    # plt.show()
    st.pyplot(x)
    



# st.title('HireMe')
#add picture
image = Image.open('hireme_logo_cropped.png')
st.image(image)

uploaded_file = st.file_uploader("Drop your resume here", type=['pdf'])
new_data = None
if uploaded_file is not None:
    
    data = ResumeParser('Resume.pdf').get_extracted_data()
    new_data = data['skills']
    new_data = [' '.join(new_data)]
    new_data = [s.lower() for s in new_data]
    new_data = [''.join(c for c in s if c.isalnum() or c==' ') for s in new_data]
    recommend(new_data)



# st.write('Your skills are: ', new_data)
    

