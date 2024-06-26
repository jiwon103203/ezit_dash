import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
from collections import defaultdict
from datetime import datetime as dt
from collections import Counter
import os
from streamlit_apexjs import st_apexcharts
import numpy as np

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
    db = firestore.client()
    return db

def bring_user(db):
    user_dict=[doc.to_dict() for doc in db.collection("users").stream()]
    return user_dict

def data_process(db,user_dict):
    user_data=defaultdict(list)
    for user in user_dict:
        try:
            user_enter_date=dt(user.get("start_time").year,user.get("start_time").month,user.get("start_time").day)
        except:
            user_enter_date=None
        #나이 구하기
        user_age=(dt.today()-dt.strptime(user.get("birthday"),"%Y-%m-%d")).days//365 if user.get("birthday") is not None else None
        user_gender=user.get("gender")
        user_interest=user.get("categ")
        user_turn=user.get("turn")
        user_play=user.get("play_num")
        user_prefer=user.get("satisfied")

        user_data["user_enter_date"].append(user_enter_date)
        user_data["user_age"].append(user_age)
        user_data["user_gender"].append(user_gender)
        user_data["user_interest"].append(user_interest)
        user_data["user_turn"].append(user_turn)
        user_data["user_play"].append(user_play)
        user_data["user_prefer"].append(user_prefer)
    return user_data


def main():
    st.header("앱대쉬보드:fire:")
    password=st.text_input("Enter password:",type="password")
    if password!=os.environ["dbpassword"]:
        st.write("<span style='color:red'>**Invalid password**</span>", unsafe_allow_html=True)
        return
    else:
        db=connect_db()
        user_dict=bring_user(db)
        data=data_process(db,user_dict)
        translate_dict={"user_enter_date":"**고객유입**","user_gender":"성별","user_interest":"관심사","user_turn":"플레이 횟수","user_play":"대화양","user_prefer":"만족도","user_age":"나이"}
        for key, value in data.items():
            if key in ["user_gender","user_interest","user_prefer"]:
                options = {
                    "chart": {
                        "toolbar": {
                            "show": False
                        }
                    },

                    "labels": pd.Series(data[key]).value_counts().index.tolist()
                    ,
                    "legend": {
                        "show": True,
                        "position": "bottom",
                    }
                }

                series = pd.Series(data[key]).value_counts().tolist()
                st_apexcharts(options, series, 'donut', '400', translate_dict[key])
            elif key in ["user_turn","user_play"]:
                temp_val=list(map(lambda x,y,z,w : x+y+z+w,[1 if t>10 else 0 for t in data[key]],[1 if t>20 else 0 for t in data[key]],[1 if t>30 else 0 for t in data[key]],[1 if t>40 else 0 for t in data[key]]))
                options = {
                    "chart": {
                        "toolbar": {
                            "show": False
                        }
                    },
                    "labels": ["10회미만","10회이상","20회이상","30회이상","40회이상"],
                    "legend": {
                        "show": True,
                        "position": "bottom",
                    }
                }
                series = pd.Series(temp_val).value_counts().tolist()
                info_string=f"__최댓값:{max(data[key])}, 최솟값:{min(data[key])}, 평균값:{round(np.mean(data[key]),2)}, 중앙값:{np.median(data[key])}"
                st_apexcharts(options, series, 'donut', '400', translate_dict[key]+info_string)

            elif key=="user_age":
                options=options = {
                    "chart": {
                        "toolbar": {
                            "show": False
                        }
                    },
                    "labels": [str(i)+"대" for i in pd.Series([t//10*10 for t in data[key] if t is not None]).value_counts().index.tolist()],
                    "legend": {
                        "show": True,
                        "position": "bottom",
                    }
                }
                series = pd.Series([t//10*10 for t in data[key] if t is not None]).value_counts().values.tolist()
                st_apexcharts(options, series, 'donut', '400', translate_dict[key])
            elif key=="user_enter_date":
                st.write(translate_dict[key])
                temp_val={k:v for k,v in Counter(data[key]).items() if k is not None}
                time_ls=[min(temp_val.keys())+datetime.timedelta(days=i) for i in range(int((max(temp_val.keys())-min(temp_val.keys())).days)+1)]
                total_val={k:temp_val[k] if k in temp_val.keys() else 0 for k in time_ls}
                sum_val={t:sum([v for k,v in temp_val.items() if k<=t]) for t in time_ls}
                st.line_chart(pd.DataFrame({"날짜":list(sum_val.keys()),"누적유입":list(sum_val.values()),"일간유입":list(total_val.values())}),
                              x="날짜",y=["누적유입","일간유입"])
                #st.line_chart(x=[dt.strftime(min(temp_val)+datetime.timedelta(days=i),"%Y-%m-%d") for i in range(int((max(temp_val)-min(temp_val)).days)+1)],y=pd.Series([t for t in data[key] if t is not None]).value_counts().values.tolist())
                #st.line_chart(pd.Series([t for t in data[key] if t is not None]).value_counts())


if __name__=="__main__":
    try:
        main()
    except ValueError:
        st.header(":no_entry: :red[Unable to connect to the database.]")
        st.markdown(":closed_lock_with_key: Please check your key in the app page.:key:")  
    

