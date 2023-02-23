import streamlit.components.v1 as components
import streamlit as st

st.title("Our team")
# components.html("""<hr style="height:10px;border:none;color:#333;background: linear-gradient(to right, red, purple);margin-bottom: 0;" /> """)
# st.write("At HIREME, we understand the challenges of job hunting, and we\'re here to help you every step of the way. Our platform connects job seekers with their dream jobs effortlessly, so you can focus on what really matters - nailing that interview and landing your dream job.")
st.markdown('<div style="text-align: center;"><br>At HIREME, we understand the challenges of job hunting, and we\'re here to help you every step of the way. Our platform connects job seekers with their dream jobs effortlessly, so you can focus on what really matters - nailing that interview and landing your dream job.<br></div>', unsafe_allow_html=True)

st.markdown('<div style="color: gray;"><br><br>Thus, we take this opportunity to express our sincere gratitude to our amazing team - <i><a href="mailto:e21cseu0268@bennett.edu.in">Dakshi</a>, <a href="mailto:e21cseu0303@bennett.edu.in">Ganesh</a>, <a href="mailto:e21cseu0268@bennett.edu.in">Sarthak</a>, <a href="mailto:e21cseu0268@bennett.edu.in">Devansh</a></i>. Without their dedication and hard work, we wouldn\'t be able to provide such a seamless job search experience to our users. Thank you for being a part of the HIREME team!<br><br><i>If you have any questions or feedback, please don\'t hesitate to reach out to us. We are here to help you find your next career opportunity and make your job search journey a success!</i><br><br></div>', unsafe_allow_html=True)
st.markdown('<a href="mailto:dakshiegoel@gmail.com" style="display: inline-block; background-image: linear-gradient(to right, purple, blue); color: white; text-align: center; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Contact us!</a>', unsafe_allow_html=True)
