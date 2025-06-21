import streamlit as st
import os
from time import sleep
from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy as np
import io, base64


USERS = os.getenv('USERS')
USERS = USERS.replace('\n', '')


ph = st.empty()

def empty():
    ph.empty()
    sleep(0.01)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.query_params:
    query_no = st.query_params["value1"]
    query_code = st.query_params["value2"]
else:
    query_no = ""
    query_code = ""

    

if st.session_state.logged_in == False:
    #empty()
    with ph.container():
        st.write(USERS)
        #if st.query_params["code"]:
        st.header("Вход")
        card_no = st.text_input("Номер карты", value=query_no, type="password")
        code = st.text_input("Код", value=query_code, type="password")

        if st.button("Войти"):
            if f"{card_no}_{code}" in USERS.split(","):
                    #st.write("Вы существуете")
                    
                st.session_state.card_no = card_no
                st.session_state.code = code
                #st.empty()
                st.session_state.logged_in = True
                empty()
            else:
                st.write("Пользователь не найден")
                st.write(card_no)
                st.write(ascii(f"1 {card_no}_{code} 1"))
                st.write(ascii(f"1 {USERS.split(',')[1]} 1"))
                    

if st.session_state.logged_in == True: 
#    empty()
#    ph.progress(0, "Загрузка.")
#    sleep(1)
#    ph.progress(50, "Загрузка..")
#    sleep(1)
#    ph.progress(100, "Загрузка...")
#    sleep(1)
    #empty()
    with ph.container():
        #im = st.image("pic1.jpg")
        image_name = "pic_aqua.png"
        #im = Image.open("pic1.jpg")
        giant_str = st.secrets["pics"][image_name.split(".")[0]]
        im = Image.open(io.BytesIO(base64.decodebytes(bytes(giant_str, "utf-8"))))
        st.write(im.size)
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("credit-card.regular.ttf", 15)

        draw.text((80, 250), f"**** **** **** {st.session_state.card_no[-4:]}",font=font)
        st.write(im.size)
        st.write(np.array(im).shape)
        st.image(np.array(im))

        st.write(f"Ваша карта : **** **** **** {st.session_state.card_no[-4:]}")
        if st.button("Выйти"):
            st.session_state.card_no = None
            st.session_state.code = None
            #st.empty()
            st.session_state.logged_in = False
            empty()
            st.rerun()
