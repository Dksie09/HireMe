import pandas as pd
import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
import re

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
    print(html)
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
            
df = pd.DataFrame({'Company Name':company_name, 'Job Title':job_title, 'About Company':about_company, 'Location':location, 'Skills Required':skills_reqd, 'Job responsibilities':job_responsibilities, 'Job requirements':job_requirements, 'Job responsibilities':job_responsibilities, 'Job responsibilities':job_responsibilities, 'Logo':logo})
print(df.head(5))
print("shape: ",df.shape)

# print("Unique: ",df.unique())
#check duplicates
print("Duplicates: ",df.info())
#check null values
print("Null values: ",df.isnull().sum())

df["Location"] = df["Location"].apply(lambda x: ' '.join(x))
df["Job responsibilities"] = df["Job responsibilities"].apply(lambda x: ' '.join(x))
df["Job requirements"] = df["Job requirements"].apply(lambda x: ' '.join(x))
df['Skills Required'] = df['Skills Required'].str.replace(',', ' ')


x = df['Job Title'].str.replace(' ', '')

df['Tags'] = df['Job Title'] + ', ' + df['Skills Required']

df['Tags'] = df['Tags'].str.replace('/', ' ')
df_new=df.drop(['Job responsibilities', 'Job requirements'], axis=1)
# df_new.head()


def remove_comma(string):
    return string.replace(',', ' ')

df_new["Tags"] = df_new["Tags"].apply(remove_comma)


import nltk
# from nltk.stem.porter import PorterStemmer
# ps = PorterStemmer()

def stem(text):
    y=[]
    for i in text.split():
        y.append(i.lower())
    return ' '.join(y)

df_new['Tags'] = df_new['Tags'].apply(stem)
df_new.drop_duplicates(inplace=True)
import pickle

pickle.dump(df_new, open('df_new.pkl','wb'))

#to csv
df_new.to_csv('company_info.csv', index=False)

    # print(len(company_name))
