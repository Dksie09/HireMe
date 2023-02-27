import pandas as pd
import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
import re
import string
from nltk.corpus import stopwords
import pickle

company_name=[]
logo = []
job_title=[]
l = []
location = []
skills_reqd=[]
about_company=[]
job_responsibilities=[]
job_requirements=[]
l2=[]
l1=[]
for i in range(1, 21):
    # driver = webdriver.Chrome()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)AppleWebkit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}
    html = requests.get('https://internshala.com/internships/engineering-internship/page-{}/'.format(i),headers=headers).text
    print(i)
    # driver.get('https://internshala.com/internships/engineering-internship/page-{}/'.format(i))

    # html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    for i in soup.find_all('a', class_='link_display_like_text view_detail_button'):
        company_name.append(i.text.strip())

    for i in soup.find_all('h3', class_='heading_4_5 profile'):
        job_title.append(i.text.strip())
    for p in soup.find_all('p', id="location_names"):
        for i in p.find('a', class_="location_link view_detail_button"):
            l.append(i.text.strip())
        location.append(l)
        l = []
    for div in soup.find_all('div', id="location_names"):
        for i in div.find('a', class_="location_link view_detail_button"):
            l.append(i.text.strip())
        location.append(l)
        l = []
    for i in soup.find_all('div', class_='internship_logo'):
        try:
            logo.append("https://internshala.com"+i.img['src'])
        except:
            logo.append("https://images1-fabric.practo.com/dermafollix-hair-transplant-and-skin-clinic-surat-1449058531-565ee0e388f5a.png")
    
    for div in soup.find_all('div', class_="cta_container"):
        url = "https://internshala.com/"+div.find('a')['href']
        web2 = requests.get(url).text
        # print(url)
        #-------------------------------------------------------------------------------------
        soup2 = BeautifulSoup(web2, 'lxml')
        if(soup2.find('div', class_='section_heading heading_5_5 skills_heading')):
            for i in soup2.find_all('div', class_='round_tabs_container'):
                    skills_reqd.append(i.text.strip().replace('\n', ', ').replace('\r', '')+" ")
                    break
        else:
            skills_reqd.append(" ")
        for i in soup2.find_all('div', class_='text-container about_company_text_container'):
            about_company.append(i.text.strip())
        #-------------------------------------------------------------------------------------
        for div2 in soup2.find_all('div', class_='internship_details'):
                # count+=1
            for i in div2.select("div[class='text-container']"):
                txt = i.text.strip()
                # print(txt)
                if("Key responsibilities:" in txt):
                    # print("yay")
                    responsibilities = txt.split("Key responsibilities:")[1].split("Requirements:")[0].strip()
                    
                    #remove index numbers from responsibilities
                    responsibilities = re.sub(r'\d+\.', '', responsibilities)
                    responsibilities = responsibilities.replace("\n", ',')
                    
                    
                    l1.append(responsibilities)
                    # print(l1)
                # if "Key responsibilities:\n" in txt:
                #     print("yay")
                    # print("----")

                if ("Requirements:" in txt):
                    requirements = txt.split("Requirements:")[1].strip()
                    requirements = re.sub(r'\d+\.', '', requirements)
                    requirements = requirements.replace("\n", ',')
                    
                    l2.append(requirements)
                    # print(l2)
            
            job_responsibilities.append(l1)
            job_requirements.append(l2)
location = [''.join(map(str, l)) for l in location]  
job_responsibilities = [''.join(map(str, l)) for l in job_responsibilities]
job_requirements = [''.join(map(str, l)) for l in job_requirements]
df = pd.DataFrame({'Company Name':company_name, 'Job Title':job_title, 'About Company':about_company, 'Location':location, 'Skills Required':skills_reqd, 'Job responsibilities':job_responsibilities, 'Job requirements':job_requirements, 'Job responsibilities':job_responsibilities, 'Job responsibilities':job_responsibilities, 'Logo':logo})
print(df.head(5))
print("shape: ",df.shape)

# print("Unique: ",df.unique())
#check duplicates
print("Duplicates: ",df.info())
#check null values
print("Null values: ",df.isnull().sum())

# df["Location"] = df["Location"].apply(lambda x: ' '.join(x))
# df["Job responsibilities"] = df["Job responsibilities"].apply(lambda x: ' '.join(x))
# df["Job requirements"] = df["Job requirements"].apply(lambda x: ' '.join(x))
# df['Skills Required'] = df['Skills Required'].str.replace(',', ' ')


x = df['Job Title'].str.replace(' ', '')

df['Tags'] = df['Job Title'] + ' ' + df['Skills Required'].str.replace(',', ' ')+' '+df["Location"].str.replace(',', ' ')# + ' '+ df["Job responsibilities"].str.replace(',', ' ') + ' ' + df["Job requirements"].str.replace(',', ' ')

#

# df['Tags'] = df['Tags'].str.replace('/', ' ')
df_new=df.drop(['Job responsibilities', 'Job requirements'], axis=1)
# df_new.head()
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
def remove_stopwords(text):
    new_text=[]
    for word in text.split():
        if word not in stopwords.words('english'):
            new_text.append(word)
    return ' '.join(new_text)


df_new["Tags"] = df_new["Tags"].apply(remove_html)
df_new["Tags"] = df_new["Tags"].apply(remove_url)
df_new["Tags"] = df_new["Tags"].apply(convert_to_pp)
df_new["Tags"] = df_new["Tags"].apply(remove_punct)
df_new["Tags"] = df_new["Tags"].apply(remove_n)
df_new["Tags"] = df_new["Tags"].apply(remove_extra_space)
df_new["Tags"] = df_new["Tags"].apply(remove_numbers)
df_new["Tags"] = df_new["Tags"].apply(remove_bullet_points)
df_new["Tags"] = df_new["Tags"].apply(remove_stopwords)
df_new["Tags"] = df_new["Tags"].apply(lambda x: remove_words_starting_with_prefix(x, '\\'))
df_new["Tags"] = df_new["Tags"].apply(remove_bullet_points)
df_new["Tags"] = df_new["Tags"].apply(remove_stopwords)

def toLowerCase(text):
    y=[]
    for i in text.split():
        y.append(i.lower())
    return ' '.join(y)

df_new['Tags'] = df_new['Tags'].apply(toLowerCase)
df_new.drop_duplicates(inplace=True)

pickle.dump(df_new, open('df_new.pkl','wb'))
print("-----pickled-----")
#to csv
df_new.to_csv('company_info.csv', index=False)
print("-----csved-----")

    # print(len(company_name))
print("----------end----------")