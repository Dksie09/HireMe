import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import requests
import os
import base64
from pyresparser import ResumeParser
from secret import TOKEN_ID

headers = {"Authorization": f"Token {TOKEN_ID}"}

#functions
def get_pdf_files(directory):
    pdf_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_files.append(os.path.join(directory, filename))
    return pdf_files

def displayPDF(file):
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.title("Enhance Resume with Github")
st.write("This is a simple app to enhance your resume with your Github profile. It will show you the languages you have used in your public repositories and their sizes. You can then add this information to your resume to show your skills.")

#add github username    
input = st.text_input("Enter your Github username")
url = f"https://api.github.com/users/{input}/repos"

if st.button("Get Github Info"):


#show resume
    st.subheader("Your Resume")
    # Define path to uploaded_resume folder
    resume_folder = "uploaded_resume"

    # Get list of PDF files from uploaded_resume folder
    pdf_files = get_pdf_files(resume_folder)

    # Display last PDF file on Streamlit app
    if len(pdf_files) > 0:
        last_resume = max(pdf_files, key=os.path.getctime)
        # st.write("Displaying last resume:", last_resume)
        displayPDF(last_resume)
        # Parse resume using pyresparser
        parser = ResumeParser(last_resume)
        result = parser.get_extracted_data()

        # Extract skills from result
        resume_skills = set(result.get("skills", []))
        
        # Display skills
        st.write("Skills found in the resume:", resume_skills)
        # os.remove(last_resume)
    else:
        st.write("No PDF files found in uploaded_resume folder.")

    #show github stats
    st.subheader("Github Info")
    st.write("This is where your Github info will be displayed")
    with st.spinner(text='Analyzing Github data...'):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            repos = response.json()
            language_sizes = {}
            total_size = 0
            for repo in repos:
                languages_url = repo["languages_url"]
                response = requests.get(languages_url, headers=headers)
                if response.status_code == 200:
                    languages = response.json()
                    size = sum(languages.values())
                    total_size += size
                    for language, language_size in languages.items():
                        if language in language_sizes:
                            language_sizes[language] += language_size
                        else:
                            language_sizes[language] = language_size
                else:
                    st.write(f"Failed to retrieve languages for repository {repo['name']}. Status code: {response.status_code}")
            cola, colb = st.columns(2)

            with cola:
                st.caption(f"Languages extracted from {input}'s public repositories:")
                language_sizes_percent = {language: round((size/total_size)*100, 2) for language, size in language_sizes.items()}
                sorted_language_sizes_percent = dict(sorted(language_sizes_percent.items(), key=lambda item: item[1], reverse=True))
                language_data = {"Language": [], "Percentage": []}
                for language, percent in sorted_language_sizes_percent.items():
                    language_data["Language"].append(language)
                    language_data["Percentage"].append(percent)
                df = pd.DataFrame(language_data)
                st.table(df)

            with colb:

                github_skills = set(language_sizes.keys())
                resume_skills = [skill.lower() for skill in resume_skills]
                github_skills = [skill.lower() for skill in github_skills]

                new_skills = set(github_skills) - set(resume_skills)
                if len(new_skills) > 0:
                    st.write("⚠️ Skills that can be added to your resume:")
                    for skill in new_skills:
                        st.warning(skill)
        else:
            st.write(f"Failed to retrieve repositories. Status code: {response.status_code}")

        os.remove(last_resume)
