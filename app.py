import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

def connect_db():
    firebase_key={
       "type" :os.environ["type"],
        "project_id":os.environ["project_id"],
        "private_key_id":os.environ["private_key_id"],
        "private_key":os.environ["private_key"],
        "client_email":os.environ["client_email"],
        "auth_uri":os.environ["auth_uri"],
        "token_uri":os.environ["token_uri"],
        "auth_provider_x509_cert_url":os.environ["auth_provider_x509_cert_url"],
        "client_x509_cert_url":os.environ["client_x509_cert_url"],
        "universe_domain":os.environ["universe_domain"]
    }
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

def main():
    key = st.text_input("Enter key:")
    col1,col2,col3=st.columns([0.2,0.2,0.6])
    with col1:
        dashboard=st.button("유저통계",key="dashboard")
    with col2:
        appdash=st.button("텍스트 분석",key="appdash")
    with col3:
        pass
    password=os.environ["password"]
    try:
        with st.sidebar:
            st.subheader("마음먹기 프로젝트")
        if dashboard:
            if key!=password:
                st.write("<span style='color:red'>**Invalid key**</span>", unsafe_allow_html=True)
            else:
                db = connect_db()
                st.switch_page("./pages/appdash.py")
        elif appdash:
            if key!=password:
                st.write("<span style='color:red'>**Invalid key**</span>", unsafe_allow_html=True)
            else:
                db = connect_db()
                st.markdown("준비중")
    except ValueError:
        st.markdown(":pushpin: 정상적으로 로그인 되었으니 좌측 <strong>:red['대쉬보드']</strong>를 눌러주세요.", unsafe_allow_html=True)
if __name__=="__main__":
    main()
