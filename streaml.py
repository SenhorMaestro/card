import streamlit as st
import os, io, base64
from time import sleep
from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy as np
from sqlalchemy.sql import text
from streamlit_echarts import st_echarts
from datetime import datetime, timedelta, timezone
import math
import random
from pathlib import Path

st.markdown("""
<style>
    * {
       overflow-anchor: none !important;
       }
</style>""", unsafe_allow_html=True)

USERS = st.secrets['USERS'] #os.getenv('USERS')
USERS = USERS.replace('\n', '')

VER =  st.secrets['VER'] #os.getenv('VER')
VER3 =st.secrets['VER3']

#VER2 = os.getenv('VER2')
dev_mode = 0

RATES = st.secrets['rates']

SALARY = st.secrets['SALARY']
BONUSES = st.secrets['BONUSES']
BONUS_OPTIONS = st.secrets['BONUS_OPTIONS']['opt1']

#st.logo("IMG_5297.PNG", size='large')
logo_image_name = "pic_logo.png"
giant_str_logo = st.secrets["pics"][logo_image_name.split(".")[0]]
im_logo = Image.open(io.BytesIO(base64.decodebytes(bytes(giant_str_logo, "utf-8"))))
st.logo(np.array(im_logo), size='large')

# Initialize connection.
# conn = st.connection("neon", type="sql")

# # Perform query.
# df = conn.query('SELECT * FROM cards;', ttl="10m")
# st.write(df)


ph = st.empty()

def empty():
    ph.empty()
    sleep(0.01)

# def disable(b):
#     st.session_state["disabled"] = b
def decode(encoded_str: str) -> str:
    core = encoded_str[st.secrets['D1']:]
    original_chars = core[::st.secrets['D2']]
    return original_chars

def s_1(data: bytes, s: int) -> bytes:
    s = st.secrets['s']
    random.seed(s)
    return bytes(b ^ random.randint(0, 255) for b in data)

@st.cache_data
def l_1(p1: str, p2: str):
    
    s = st.secrets['s']
    l = st.secrets["ps"][p1]
    r = Path("i/"+p2).read_text(encoding='utf-8')
    f = l + r
    i = base64.b64decode(f)
    i = s_1(i, s)

    return i

def disable():
    st.session_state.disabled = True

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def form_noun(number, noun_forms):
    """
    Согласует числительное и существительное в русском языке.
    Args:
        number: Числительное (целое число).
        noun_forms: Список форм существительного (например, ["товар", "товара", "товаров"]).
    Returns:
        Строка, содержащая согласованное существительное.
    """
    number = -number if number < 0 else number
    
    if number % 1 == 0:
        if 11 <= number % 100 <= 14:
            return noun_forms[2]
        elif number % 10 == 1:
            return noun_forms[0]
        elif 2 <= number % 10 <= 4:
            return noun_forms[1]
        else:
            return noun_forms[2]
    else: #not int
        return noun_forms[1]
    
def balance_updating(last_login_time):
     
    last_login_utc = last_login_time - timedelta(hours=st.secrets['tzs']['hours_to_utc'])
    now_utc = datetime.now() - timedelta(hours=st.secrets['tzs']['hours_to_utc'])
    if dev_mode:
        st.write(f"last_login_utc: {last_login_utc}")
        st.write(f"now_utc: {now_utc}")

    if now_utc.date() > last_login_utc.date():
        # вход был вчера
        if dev_mode:
            st.write("situation1")
        update_last_login = True
        reset_balance = True
    else:
        if dev_mode: 
            st.write("situation2")
        update_last_login = False
        reset_balance = False

        
    if update_last_login == True and reset_balance == True:
        if dev_mode:
            st.write("sql1")
        with conn.session as s:
            task = f'''UPDATE cards
            SET
                play_start = NOW() + INTERVAL '{st.secrets['tzs']['HOURS']} hours',
                balance = 0
            WHERE card_no = :card_no;'''

            s.execute(text(task), 
            #ttl="10m",
            params={"card_no": st.session_state.card_no},)
        
            s.commit()
    # elif update_last_login == True and reset_balance == False:
    #     st.write("sql2")
    #     with conn.session as s:
    #         task = '''UPDATE cards
    #         SET
    #             play_start = NOW() + INTERVAL '3 hours'
    #         WHERE card_no = :card_no;'''

    #         s.execute(text(task), 
    #         #ttl="10m",
    #         params={"card_no": st.session_state.card_no},)
    #         s.commit()

def check_null(last_login_time):
    if last_login_time is None:
        if st.session_state.card_no[4:7] in ['338']:
            update_play_reg_query = f", play_reg = NOW() + INTERVAL '{st.secrets['tzs']['HOURS']} hours'"
            second_balance_setting = f", second_balance = 0"
        else:
            update_play_reg_query = ''
            second_balance_setting = ''

    
        with conn.session as s:
            task = f'''UPDATE cards
            SET
                play_start = NOW() + INTERVAL '{st.secrets['tzs']['HOURS']} hours'
                {update_play_reg_query}
                {second_balance_setting}
            WHERE card_no = :card_no 
            '''

            s.execute(text(task), 
            #ttl="10m",
            params={"card_no": st.session_state.card_no},)
        
            s.commit()
            df = conn.query('SELECT * FROM cards WHERE card_no = :card_no;', 
                    show_spinner="Настройка безопасного соединения...",
                    ttl=0,#None, #"10m",
                    params={"card_no": st.session_state.card_no},)
            new_last_login_time = df['play_start'][0]
        st.write("С первым входом вас!!!")
        st.write(new_last_login_time)
        return new_last_login_time
    else:
        return last_login_time
    
def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    amount_in_target = amount * RATES[to_currency] / RATES[from_currency] 
    
    return math.floor(amount_in_target*100)/100

def convert_currency2(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    amount_in_target = amount * RATES[to_currency] / RATES[from_currency] 
   
    return math.ceil(amount_in_target*100)/100

def convert_currency_real(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount

    amount_in_target = amount * RATES[to_currency] / RATES[from_currency] 
    
    return amount_in_target

def on_from_currency_change():
    # Просто перерасчет amount_to по текущему amount_from
    amount = st.session_state.amount_from
    if amount < 0.01:
        amount = 0.01
        st.session_state.amount_from = amount
    st.session_state.active_input = 'amount_from'
    st.session_state.amount_to = convert_currency(
        amount,
        st.session_state.from_currency,
        st.session_state.to_currency
    )

def on_to_currency_change():
    # Аналогично для смены валюты получателя
    amount = st.session_state.amount_from
    if amount < 0.01:
        amount = 0.01
        st.session_state.amount_from = amount
    st.session_state.active_input = 'amount_from'
    st.session_state.amount_to = convert_currency(
        amount,
        st.session_state.from_currency,
        st.session_state.to_currency
    )

def on_amount_from_change():
    # Пользователь меняет левое поле — считаем правое
    st.session_state.active_input = 'amount_from'
    amount = st.session_state.amount_from
    if amount < 0.01:
        amount = 0.01
        st.session_state.amount_from = amount
    st.session_state.amount_to = convert_currency(
        amount,
        st.session_state.from_currency,
        st.session_state.to_currency
    )

def on_amount_to_change():
    # Пользователь меняет правое поле — считаем левое
    st.session_state.active_input = 'amount_to'
    amount = st.session_state.amount_to
    if amount < 0.01:
        amount = 0.01
        st.session_state.amount_to = amount
    st.session_state.amount_from = convert_currency2(
        amount,
        st.session_state.to_currency,
        st.session_state.from_currency
    )

def int_float_calc(balance_int: int, balance_cents: int, amount: float):
    """
    balance_int, balance_cents  — текущее состояние счёта (0 <= balance_cents < 100)
    amount                      — положительная (пополнение) или отрицательная (списание) сумма,
                                   с точностью до 2 знаков после точки.
    Возвращает (new_int, new_cents) в том же формате.
    """
    # переводим amount в "центовые" единицы
    amount_cents = int(round(amount * 100))

    # складываем всё в одну переменную
    total_cents = balance_int * 100 + balance_cents + amount_cents

    # обратно разбиваем на целые рубли (demand) и центы
    new_balance_int = total_cents // 100
    new_balance_cents = total_cents % 100
    return new_balance_int, new_balance_cents

def upd(balance_name, cents_name, new_balance_int, new_balance_cents, card):
        #            sign = "-" или "+"
                    
        #                      SQL UPDATE cards
        #                      SET 
        #                {balance_name} = 
        #               {balance_name}{sign}{sum_2_int},
        #                 {cents_name} =
        #              {cents_name}{sign}{ssum_2_cents}

        #                     WHERE card_no = : card_to 
        #                                      (Или st.ses.card_no)

    with conn.session as s:
        task = f'''UPDATE cards
            SET
                {balance_name} = {new_balance_int}, 
                {cents_name} = {new_balance_cents}
            WHERE card_no = {card};
            '''
        s.execute(text(task), 
        #ttl="10m",
        )
    
        s.commit()

def success_transfer_classic(card_to, ammount, cur):
    return st.success(
        f"""Перевод выполнен успешно.  \n

        Отправлено: {ammount} {cur}  \n

        Получатель : {card_to}  \n

        Время : {(datetime.now() + timedelta(hours=st.secrets['tzs']['hours_to_local'])).strftime('%d.%m.%Y %H:%M:%S')}  \n

        Заскриньте этот чек, если он вам нужен, так как мы не храним информацию о переводах.  \n

        Если баланс не обновился, попробуйте скрыть-показать его с помощью ползунка 'Показать/скрыть баланс'.
        """
        )

def success_transfer(card_to, selection):
    
    if selection == "Оплатить/Перевести валюту":
        return st.success(
        f"""Перевод выполнен успешно.  \n

        Отправлено: {st.session_state.amount_from} {st.session_state.from_currency}  \n

        Зачислено получателю: {st.session_state.amount_to} {st.session_state.to_currency}  \n

        Получатель : {card_to}  \n

        Время : {(datetime.now() + timedelta(hours=st.secrets['tzs']['hours_to_local'])).strftime('%d.%m.%Y %H:%M:%S')}  \n

        Заскриньте этот чек, если он вам нужен, так как мы не храним информацию о переводах.  \n

        Если баланс не обновился, попробуйте скрыть-показать его с помощью ползунка 'Показать/скрыть баланс'.
        """
        )
    elif selection == "Перевести между своими счетами":
        return st.success(
        f"""Успешно перевели деньги между счетами.  \n

        Списано со счёта в {st.session_state.from_currency}: {st.session_state.amount_from} {st.session_state.from_currency}  \n

        Зачислено на счёт в {st.session_state.to_currency}: {st.session_state.amount_to} {st.session_state.to_currency}  \n

        Время : {(datetime.now() + timedelta(hours=st.secrets['tzs']['hours_to_local'])).strftime('%d.%m.%Y %H:%M:%S')}  \n

        Заскриньте этот чек, если он вам нужен, так как мы не храним информацию о переводах.  \n

        Если баланс не обновился, попробуйте скрыть-показать его с помощью ползунка 'Показать/скрыть баланс'.
        """
        )

def salary_update(balance_name, salary, extra_query):   
    with conn.session as s:
        task = f'''UPDATE cards
                SET 
                {balance_name} = {balance_name} + {salary}
                {extra_query}
                ,play_start = NOW() + INTERVAL '{st.secrets['tzs']['HOURS']} hours'
                WHERE card_no = :card_no;'''

        s.execute(text(task), 
                #ttl="10m",
                params={"card_no": st.session_state.card_no},)
    
        s.commit()

# if 'from_currency' not in st.session_state:
#     st.session_state.from_currency = 'UNI'
# if 'to_currency' not in st.session_state:
#     st.session_state.to_currency = 'HRD'
# if 'amount_from' not in st.session_state:
#     st.session_state.amount_from = 1.00
# if 'amount_to' not in st.session_state:
#     st.session_state.amount_to = convert_currency(
#         st.session_state.amount_from,
#         st.session_state.from_currency,
#         st.session_state.to_currency
#     )
if "show_card_no" not in st.session_state:
    st.session_state.show_card_no = False

if 'active_input' not in st.session_state:
    st.session_state.active_input = 'amount_from'

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "block_login_screen" not in st.session_state:
    st.session_state.block_login_screen = False

if "disabled" not in st.session_state:
    st.session_state.disabled = False

if "value1" in st.query_params:
    query_no = decode(st.query_params["value1"])
else: 
    query_no = ""
if "value2" in st.query_params:   
    query_code = decode(st.query_params["value2"])
else:
    query_code = ""

if "dev_mode" in st.query_params:
    dev_mode = decode(st.query_params["dev_mode"])
    if dev_mode == st.secrets["DEVMODE"]:
        dev_mode = 1
    else:
        dev_mode = 0

if "value5" in st.query_params: #instant_plus_balance

    st.session_state.block_login_screen = True
    st.session_state.card_no = query_no

    instant_ammount = decode(st.query_params["value5"])

    conn = st.connection("neon", type="sql")

    if st.session_state.card_no[4:7] in ['127', '338']:

        # Perform query.
        df = conn.query('SELECT * FROM cards WHERE card_no = :card_no;', 
                        show_spinner="Настройка безопасного соединения...",
                        ttl=0,#None, #"10m",
                        params={"card_no": st.session_state.card_no},)
        if dev_mode:
            st.write(df)
            
        if st.session_state.card_no[4:7] in ['338']:
            update_second_balance_query = f", second_balance = second_balance + {str(instant_ammount)}"
        else:
            update_second_balance_query = ''

        last_login_time = df['play_start'][0]
        last_login_time =check_null(last_login_time)
        balance_updating(last_login_time)
        with conn.session as s:
            task = f'''UPDATE cards
            SET
                balance = balance + {str(instant_ammount)}
                {update_second_balance_query}
            WHERE card_no = :card_no;'''

            s.execute(text(task), 
                    #ttl="10m",
                    params={"card_no": st.session_state.card_no},)
        
            s.commit()

        st.write(f"Карта ****   ****   ****   {st.session_state.card_no[-4:]} успешно пополнена.")

        st.link_button("На главную", st.secrets["main_page"])

    elif st.session_state.card_no[4:7] in ['584']:

        df = conn.query('SELECT * FROM cards WHERE card_no = :card_no;', 
                        show_spinner="Настройка безопасного соединения...",
                        ttl=0,#None, #"10m",
                        params={"card_no": st.session_state.card_no},)
        
        if df['play_start'][0] is None:
            with conn.session as s:
                task = f'''UPDATE cards
                        SET 
                            play_start = NOW()
                        WHERE card_no = :card_no;'''

                s.execute(text(task), 
                        #ttl="10m",
                        params={"card_no": st.session_state.card_no},)
            
                s.commit()

            st.write(f"Начали отсчёт времени по карте ****   ****   ****   {st.session_state.card_no[-4:]}.")
            st.link_button("В личный кабинет", f"{st.secrets['main_page']}/?value1={st.session_state.card_no}&value2={query_code}")
        else:
            #disabled =False
            if st.session_state.disabled == False:
                #with ph.container():
                with ph.form("form0"):

                        st.write("Для подтверждения остановки таймера требуется код взрослика")
                        verif_code = st.text_input("Код", value="", type="password", 
                                                #disabled=disabled
                                                #disabled=st.session_state.get("disabled", True)
                                                #disabled=st.session_state.disabled
                                                )
                        # if verif_code == st.secrets['VER2'][st.session_state.card_no]:
                        #     on_click=disable()
                        # else:
                        #     on_click=None

                        # if st.button("Подтвердить",
                        #              #on_click=disable, 
                        #              #disabled=st.session_state.disabled 
                        #             #disabled=disabled
                        #             #disabled=st.session_state.get("disabled", True)
                        #             #disabled=st.session_state.disabled
                        #             ):
                        pressed = st.form_submit_button("Подтвердить",
                                                        disabled=st.session_state.disabled,
                                                        enter_to_submit=False)
                        if pressed and verif_code == st.secrets['VER2'][st.session_state.card_no]:
                            with conn.session as s:
                                task = f'''UPDATE cards
                                        SET 
                                        balance = balance - ROUND(EXTRACT(EPOCH FROM (NOW() - play_start)) / 60),
                                        play_start = NULL
                                        WHERE card_no = :card_no;'''

                                s.execute(text(task), 
                                        #ttl="10m",
                                        params={"card_no": st.session_state.card_no},)
                            
                                s.commit()
                            #st.write(f"Успешно списали время по карте ****   ****   ****   {st.session_state.card_no[-4:]}.")
                            #disabled = True
                            #st.session_state.disabled = True
                            #sleep(0.5)

                            #empty()
                            st.session_state.disabled = True
                            #st.write("Успешно")
                            empty()
                        #else:
                        elif pressed and verif_code != st.secrets['VER2'][st.session_state.card_no]:
                            st.write("Код взрослика не верный. Таймер не остановлен. Попробуйте ещё раз")

            if st.session_state.disabled == True:
                    st.write(f"Успешно списали время по карте ****   ****   ****   {st.session_state.card_no[-4:]}.")
                    st.link_button("В личный кабинет", f"{st.secrets['main_page']}/?value1={st.session_state.card_no}&value2={query_code}")
            

            



if st.session_state.logged_in == False and st.session_state.block_login_screen == False:
    #empty()
    with ph.container():
        if dev_mode:
            st.write(USERS)
        #st.write(st.secrets["sm_codes"])
        #st.write(st.secrets["ser_types"])

        st.header("Вход")
        card_no = st.text_input("Номер карты", value=query_no, type="password")
        code = st.text_input("Код", value=query_code, type="password")

        if st.button("Войти"):
            if len(card_no) == 5:
                card_no = 11*"0" + card_no

            if f"{card_no}_{code}" in USERS.split(","):
                    #st.write("Вы существуете")
                    
                st.session_state.card_no = card_no
                st.session_state.code = code
                #st.empty()
                st.session_state.logged_in = True
                empty()
            else:
                st.write("Пользователь не найден")
                #st.write(card_no)
                #st.write(ascii(f"1 {card_no}_{code} 1"))
                #st.write(ascii(f"1 {USERS.split(',')[1]} 1"))
                    

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
        #Initialize connection.
        
        conn = st.connection("neon", type="sql")

        # Perform query.
        df = conn.query('SELECT * FROM cards WHERE card_no = :card_no;', 
                        show_spinner="Настройка безопасного соединения...",
                        ttl=0,#None, #"10m",
                        params={"card_no": st.session_state.card_no},)
        if dev_mode:
            st.write(df)
        #st.write(df["balance"][0])

        #Проверка непустого значения
        if st.session_state.card_no[4:7] in ['127', '338']:
            last_login_time = df['play_start'][0]
            last_login_time = check_null(last_login_time)
            

        # if st.session_state.card_no[4:7] in ['127', '338']:
        #     last_login_time = df['play_start'][0]
            #st.write( (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S") ) 
            # update_time = datetime.now().replace(hour=3, minute=0, second=0, microsecond=0) 
            # zero_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # if dev_mode:
            #     st.write(last_login_time)
            #     st.write(update_time)
            #     st.write(zero_time)
            
            balance_updating(last_login_time)

        if st.session_state.card_no[4:7] in ['777']:
            if datetime.now().month != (df['play_start'][0]).month:
                # st.write(datetime.now().month)
                # st.write((df['play_start'][0]).month)
                num_month = diff_month(datetime.now(), df['play_start'][0])
                salary_update("balance", SALARY*num_month, f", cents_1 = cents_1 + {BONUSES*num_month}")
                st.toast("Начислена зарплата", icon='🎉')
                st.balloons()

        st.header("Личный кабинет пользователя", divider='gray')

        @st.fragment
        def main_columns():
            left_col, right_col = st.columns([0.65, 0.35]) #st.columns(2)
            
            with right_col:
                
                show_card_no = st.toggle("Показать/скрыть номер карты")
                
                show_sm_code = st.toggle(f"Показать/скрыть {st.secrets['sm_codes'][st.session_state.card_no[7:8]]}-код")
                column1,  column3 = st.columns([0.10,0.90], gap=None, vertical_alignment="bottom")
                sm_image_name = f"sm_{st.session_state.card_no[7:8]}.png"

                image_bytes = l_1(sm_image_name.split('.')[0], f"{sm_image_name.split('.')[0]}.txt")
                
                column1.image(image_bytes, width=50)

                if show_sm_code:
                    column3.badge(st.session_state.code, color="green", 
                                )
                else:
                    column3.badge("****", color="red", 
                                )


                st.write(f"Тип карты : *{st.secrets['ser_types'][st.session_state.card_no[4:7]]}*")

            with left_col:
                @st.cache_data
                def init_img(show_card_no, card_no): #card_no не используется, нужен только, чтобы для разных пользователей на одном устройстве не кешировался один вариант номера
                    
                    if st.session_state.card_no[4:7] in ['127']:
                        image_name = "pic_aqua.png"
                        
                    else:
                        image_name = "pic_classic.png"

                    giant_str = st.secrets["pics"][image_name.split(".")[0]]
                    im = Image.open(io.BytesIO(base64.decodebytes(bytes(giant_str, "utf-8"))))

                    draw = ImageDraw.Draw(im)
                    #font = ImageFont.truetype("credit-card.regular.ttf", 50)
                    font = ImageFont.truetype("helvetica-rounded-bold.ttf", 80)
                    #font = ImageFont.truetype("CREDC___.ttf", 60)
                    if show_card_no: #show_card_no:
                        if st.session_state.card_no[0:7] == 7*"0":
                            draw.text((200, 760), f"{st.session_state.card_no[0:4]}   {st.session_state.card_no[4:8]}   {st.session_state.card_no[8:12]}   {st.session_state.card_no[12:]}",
                                font=font, fill=(0,0,0), spacing=20, align="right"
                                )
                        else:
                            draw.text((240, 760), f"{st.session_state.card_no[0:4]}   {st.session_state.card_no[4:8]}   {st.session_state.card_no[8:12]}   {st.session_state.card_no[12:]}",
                                font=font, fill=(0,0,0), spacing=20, align="right"
                                )
                        
                    else:

                        draw.text((280, 760), f" ****   ****   ****   {st.session_state.card_no[-4:]}",
                                font=font, fill=(0,0,0), spacing=20, align="right"
                                )

                    st.image(np.array(im), width=500)
                    

                init_img(show_card_no, st.session_state.card_no)

        main_columns()
        #st.write(f"Тип карты : *{st.secrets['ser_types'][st.session_state.card_no[4:7]]}*")

        expander = st.expander("Подробнее о карте")
        expander.write(st.secrets['bios'][st.session_state.card_no[4:7]])

        balance_left_col, balance_right_col = st.columns([0.65, 0.35])

        with balance_right_col:
            show_bal = st.toggle("Показать/скрыть баланс")

        with balance_left_col:
            if show_bal:
                #st.write(f"Баланс: {df['balance'][0]} {form_noun(df['balance'][0], st.secrets.cur[df['currency'][0]]['forms'])}")
                if st.session_state.card_no[4:7] in ["584"]:
                    st.metric(label="Баланс :", 
                        value=f"{int(df['balance'][0]/60)} {form_noun(int(df['balance'][0]/60), st.secrets.cur['HRS']['forms'])} {int(df['balance'][0]%60)} {form_noun(int(df['balance'][0]%60), st.secrets.cur['MIN']['forms'])}",
                        border=True)
                elif st.session_state.card_no[4:7] in ["253"]:
                    #c1, c2, c3 = st.columns([1, 1, 1], gap="small", vertical_alignment="bottom")
                    st.metric(label="Счёт 1 :", 
                        value=f"{(df['balance'][0]+df['cents_1'][0]/100):.2f} {df['currency'][0]}",
                        border=True)
                    st.caption(f"{df['currency'][0]} = {st.secrets.cur[df['currency'][0]]['forms'][4]}")
                    st.metric(label="Счёт 2 :", 
                        value=f"{(df['second_balance'][0]+df['cents_2'][0]/100):.2f} {df['currency_2'][0]}",
                        border=True)
                    st.caption(f"{df['currency_2'][0]} = {st.secrets.cur[df['currency_2'][0]]['forms'][4]}")
                    st.metric(label="Счёт 3 :", 
                        value=f"{(df['third_balance'][0]+df['cents_3'][0]/100):.2f} {df['currency_3'][0]}",
                        border=True)
                    st.caption(f"{df['currency_3'][0]} = {st.secrets.cur[df['currency_3'][0]]['forms'][4]}")
                elif st.session_state.card_no[4:7] in ["338"]:
                    st.metric(label="Баланс* :", 
                        value=f"{df['second_balance'][0]} {form_noun(df['second_balance'][0], st.secrets.cur[df['currency'][0]]['forms'])}",
                        border=True)
                elif st.session_state.card_no[4:7] in ["777"]:
                    st.metric(label="Баланс :", 
                        value=f"{df['balance'][0]} {form_noun(df['balance'][0], st.secrets.cur[df['currency'][0]]['forms'])}",
                        border=True)
                    st.metric(label="Всего чокобонусов :", 
                        value=f"{df['cents_1'][0]} {form_noun(df['cents_1'][0], st.secrets.cur['BON']['forms'])}",
                        border=True)
                else:
                    st.metric(label="Баланс :", 
                        value=f"{df['balance'][0]} {form_noun(df['balance'][0], st.secrets.cur[df['currency'][0]]['forms'])}",
                        border=True)
            else:
                if st.session_state.card_no[4:7] in ["584"]:
                    st.metric(label="Баланс :", 
                        value=f"* {st.secrets.cur['HRS']['forms'][2]} ** {st.secrets.cur['MIN']['forms'][2]}",
                        border=True)
                #st.write(f"Баланс: *** {st.secrets.cur[df['currency'][0]]['forms'][2]}")
                elif st.session_state.card_no[4:7] in ["253"]:
                    #c1, c2, c3 = st.columns([1, 1, 1], gap="small", vertical_alignment="bottom")
                    st.metric(label="Счёт 1 :", 
                        value=f"*** {df['currency'][0]}",
                        border=True)
                    st.caption(f"{df['currency'][0]} = {st.secrets.cur[df['currency'][0]]['forms'][4]}")
                    st.metric(label="Счёт 2 :", 
                        value=f"*** {df['currency_2'][0]}",
                        border=True)
                    st.caption(f"{df['currency_2'][0]} = {st.secrets.cur[df['currency_2'][0]]['forms'][4]}")
                    st.metric(label="Счёт 3 :", 
                        value=f"*** {df['currency_3'][0]}",
                        border=True)
                    st.caption(f"{df['currency_3'][0]} = {st.secrets.cur[df['currency_3'][0]]['forms'][4]}")
                elif st.session_state.card_no[4:7] in ["338"]:
                    st.metric(label="Баланс* :",
                        value=f"*** {st.secrets.cur[df['currency'][0]]['forms'][2]}",
                        border=True)
                elif st.session_state.card_no[4:7] in ["777"]:
                    st.metric(label="Баланс :",
                        value=f"*** {st.secrets.cur[df['currency'][0]]['forms'][2]}",
                        border=True)
                    st.metric(label="Всего чокобонусов :", 
                        value=f"*** {st.secrets.cur['BON']['forms'][2]}",
                        border=True)
                else:
                    st.metric(label="Баланс :",
                        value=f"*** {st.secrets.cur[df['currency'][0]]['forms'][2]}",
                        border=True)
                

        if st.session_state.card_no[4:7] in ['127']:
            st.subheader("От суточной нормы* :", divider='blue')
            liquidfill_option1 = {
                "series": [{"type": "liquidFill", "data": [df['balance'][0]/8, 
                                                        0.060*df['balance'][0], 
                                                        0.047*df['balance'][0], 
                                                        0.036*df['balance'][0]]}]
                }
            st_echarts(liquidfill_option1)
            st.caption("*Из расчёта 1 стакан приблилизительно = 250 мл и норма = 2 л")
        
        elif st.session_state.card_no[4:7] in ['338']:
            obn_col_left, obn_col_right = st.columns(2)
            with obn_col_left:
                st.metric(label="Всего накоплено за сегодня :",
                        value=f"{df['balance'][0]} {form_noun(df['balance'][0], st.secrets.cur[df['currency'][0]]['forms'])}",
                        border=True)
                st.metric(label="От суточной нормы** :",
                        value=f"{df['balance'][0]/8*100} %",
                        #delta="Вы сегодня наобнимались", 
                        border=True)
                st.caption("*Всего накоплено с момента регистрации")
                st.caption("**Из расчёта 8 обнимашек в день")
                
            with obn_col_right:
                # st.metric(label="Всего накоплено с момента регистрации:",
                #         value=f"{df['second_balance'][0]} {form_noun(df['second_balance'][0], st.secrets.cur[df['currency'][0]]['forms'])}",
                #         border=True)
                avg = df['second_balance'][0] / (((datetime.now() + timedelta(hours=st.secrets['tzs']['hours_to_local']) - df['play_reg'][0])).days + 1)
                st.metric(label="В среднем за день :",
                        value=f"{avg:.2f} {form_noun(avg, st.secrets.cur[df['currency'][0]]['forms'])}",
                        #delta=delta_str,
                        #delta_color = "off",
                        border=True)
                # st.write(delta_str)
                # st.write(delta_str2)
                days_since_reg = ((((datetime.now() + timedelta(hours=st.secrets['tzs']['hours_to_local'])).replace(hour=0, minute=0, second=0, microsecond=0) - (df['play_reg'][0]).replace(hour=0, minute=0, second=0, microsecond=0))).days + 1)
                delta_per_day = (8-avg)*days_since_reg
                delta_total = 8*days_since_reg
                if delta_per_day > 0:
                    delta_str = f"Вам недодато в среднем за день {8-avg:.2f} {form_noun(8-avg, st.secrets.cur[df['currency'][0]]['forms'])}"
                    #delta_str2 = f"Вам недодато {delta_total-df['second_balance'][0]} {form_noun(delta_total-df['second_balance'][0], st.secrets.cur[df['currency'][0]]['forms'])} за всё время"
                    st.metric(label="Вам недодато за всё время:",
                        value=f"{delta_total-df['second_balance'][0]} {form_noun(delta_total-df['second_balance'][0], st.secrets.cur[df['currency'][0]]['forms'])}",
                        #delta=delta_str,
                        #delta_color = "inverse",
                        border=True)
                else:
                    st.metric(label="Перевыполнили норму на:",
                        value=f"{abs(-delta_per_day)} {form_noun(abs(-delta_per_day), st.secrets.cur[df['currency'][0]]['forms'])}",
                        #delta=delta_str,
                        #delta_color = "off",
                        border=True)
                    #delta_str = f"Перевыполнили норму на {-delta_per_day:.2f}"
                    delta_str = "Вы обнимаетесь достаточно. Так держать!!!"


                # st.metric(label="В среднем за день:",
                #         value=f"{avg:.2f} {form_noun(avg, st.secrets.cur[df['currency'][0]]['forms'])}",
                #         #delta=delta_str,
                #         #delta_color = "off",
                #         border=True)
                st.caption(delta_str)
                #st.write(delta_str2)

        
        

        #st.write(f"Ваша карта : **** **** **** {st.session_state.card_no[-4:]}")

        if st.session_state.card_no[4:7] in ['127','338']: #AQUA
            variants = ["Пополнить"]
            verif_bank = VER
            #on_change_selector = None
        elif st.session_state.card_no[4:7] in ['584']:
            variants = ["Пополнить/Списать", "Поделиться"]
            #on_change_selector = None
        elif st.session_state.card_no[4:7] in ['253']:
            variants = ["Пополнить счёт","Перевести между своими счетами","Оплатить/Перевести валюту","Посмотреть курсы валют"]
            #on_change_selector = on_amount_from_change
        elif st.session_state.card_no[4:7] in ['777']:
            variants = ["Пополнить", "Оплатить/Перевести", "Обменять бонусы"]
            #on_change_selector = None
        else:
            variants = ["Пополнить","Оплатить/Перевести"]
            #on_change_selector = None

        selection = st.pills("Операции", variants, selection_mode="single", 
                             #on_change=on_change_selector
                             )
        if selection == "Пополнить" or selection == "Пополнить/Списать" or selection == "Пополнить счёт":
                with st.form("my_form", clear_on_submit=True, enter_to_submit=False):
                    
                    min_val = 1
                    if st.session_state.card_no[4:7] in ['127']:
                        st.write("Здесь вы можете пополнить свой водный баланс.")
                        st.text("Счётчик сбрасывается ежедневно в 03:00")
                    elif st.session_state.card_no[4:7] in ['338']:
                        st.write("Здесь вы можете пополнить свой баланс. Карта является накопительной , списание обнимашек недоступно")
                    elif st.session_state.card_no[4:7] in ['584']:
                        st.write("Здесь взрослик может пополнить ваш баланс или списать с него минуты.")
                        st.text("Для попонения введите положительное число, для списания добавьте знак минус перед числом.")
                        st.text("Для попонения/списания необходимо ввести код взрослика.")
                        min_val = -2000000000
                    else: #classic, multi
                        st.write("Вы можете пополнить карту , отдав наличные представителю банка , который выдаст вам код подтверждения.")

                    if st.session_state.card_no[4:7] in ['127', '338']:
                        col1, col2, col3, col4 = st.columns([1, 0.2, 1, 1], gap="small", vertical_alignment="bottom")

                        balance_plus = col1.number_input(f"Введите количество {st.secrets.cur[df['currency'][0]]['forms'][2]} :", value=None, placeholder='',
                                                 step=1,
                                                 min_value=1,
                                                 max_value=2000000000)
                        if st.session_state.card_no[4:7] in ['127']:
                            col2.write(":cup_with_straw:")
                        elif st.session_state.card_no[4:7] in ['338']:
                            col2.text("") #:hearts:")

                        verif_code = col3.text_input('Введите ваш смешарик-код :', '', placeholder='ваш код',
                                                    max_chars=4,
                                                    type="password")
                        
                            #col3.write(":cup_with_straw:")
                        
                        pressed_plus = col4.form_submit_button("Подтвердить")

                    else:
                        col0, col1 = st.columns([3, 1], gap="small", vertical_alignment="bottom")

                        balance_plus = col0.number_input('Введите сумму :', value=None, placeholder='',
                                                    step=1,
                                                    min_value=min_val,
                                                    max_value=2000000000)

                        if st.session_state.card_no[4:7] in ['253']:
                            curs_list =  [df["currency"][0], df["currency_2"][0] , df["currency_3"][0]]
                            selected_cur = col1.selectbox('Валюта', curs_list)
                        else:
                            col1.write(df["currency"][0])


                        col2, col3, col4 = st.columns([1, 2, 1], gap="small", vertical_alignment="bottom")

                        verif_code = col2.text_input('Введите ваш смешарик-код :', '', placeholder='ваш код',
                                                    max_chars=4,
                                                    type="password")
                        
                            #col3.write(":cup_with_straw:")
                        if st.session_state.card_no[4:7] in ['584']:
                            help_text = 'вводится взросликом'
                        else: 
                            help_text = 'выдаётся представителем банка'

                        verif_bank = col3.text_input('Код подтверждения :', '', placeholder=help_text,
                                                    max_chars=5,
                                                    type="password")
        
                        
                        pressed_plus = col4.form_submit_button("Подтвердить")
                    

                    if pressed_plus:
                        condition = verif_code == str(df["code"][0]) and verif_bank == VER

                        if st.session_state.card_no[4:7] in ['338']:
                            update_first_balance_query = f"balance = balance + {str(balance_plus)}"
                            update_second_balance_query = f", second_balance = second_balance + {str(balance_plus)}"
                            update_third_balance_query = ''
                        elif st.session_state.card_no[4:7] in ['584']:
                            condition = verif_code == str(df["code"][0]) and verif_bank == st.secrets['VER2'][st.session_state.card_no]
                            update_first_balance_query = f"balance = balance + {str(balance_plus)}"
                            update_second_balance_query = ''
                            update_third_balance_query = ''
                        elif st.session_state.card_no[4:7] in ['253']:
                            condition = verif_code == str(df["code"][0]) and verif_bank == VER3
                            if selected_cur == curs_list[0]:
                                update_first_balance_query = f"balance = balance + {str(balance_plus)}"
                                update_second_balance_query = ''
                                update_third_balance_query = ''
                            elif selected_cur == curs_list[1]:
                                update_first_balance_query = ''
                                update_second_balance_query = f"second_balance = second_balance + {str(balance_plus)}"
                                update_third_balance_query = ''
                            elif selected_cur == curs_list[2]:
                                update_first_balance_query = ''
                                update_second_balance_query = ''
                                update_third_balance_query = f"third_balance = third_balance + {str(balance_plus)}"

                        else: #classic
                            update_first_balance_query = f"balance = balance + {str(balance_plus)}"
                            update_second_balance_query = ''
                            update_third_balance_query = ''
                        #st.write(f"look {update_second_balance_query}")
                        

                        if condition:
                            with conn.session as s:
                                s.execute(text(f'''UPDATE cards 
                                                SET {update_first_balance_query} 
                                                    {update_second_balance_query} 
                                                    {update_third_balance_query} WHERE card_no = :card_no;'''), 
                                #ttl="10m",
                                params={"card_no": st.session_state.card_no},)
                            
                                s.commit()
                            st.success("Успешно. Если баланс не обновился, попробуйте скрыть-показать его с помощью ползунка 'Показать/скрыть баланс'.")
                        else:
                            st.write("Введён неверный код")
        elif selection == "Оплатить/Перевести" or selection == "Поделиться":
                with st.form("my_form2", clear_on_submit=True, enter_to_submit=False):

                    if st.session_state.card_no[4:7] in ['584']:
                        st.write("Вы можете сделать перевод по номеру карты получателя из 16 цифр, но с разрешения взрослика (требуется код взрослика)")
                    else:
                        st.write("Вы можете сделать перевод по номеру карты получателя из 16 цифр, либо оплатить покупку в магазине с использованием 5-значного кода магазина.")

                    if st.session_state.card_no[4:7] in ['584']:
                        col0, col1 = st.columns([2, 1], gap="small", vertical_alignment="bottom")

                        balance_minus = col0.number_input('Введите сумму в минутах:', value=None, placeholder='',
                                                    step=1,
                                                    min_value=1,
                                                    max_value=2000000000)
                        verif_code_2 = col1.text_input('Введите код взрослика :', '', placeholder='для одобрения',
                                                 max_chars=5,
                                                 type="password")
                    else:
                        balance_minus = st.number_input('Введите сумму :', value=None, placeholder='',
                                                    step=1,
                                                    min_value=1,
                                                    max_value=2000000000)
                    

                    
                    col2, col3, col4 = st.columns([1, 2, 1], gap="small", vertical_alignment="bottom")

                    verif_code = col2.text_input('Введите ваш смешарик-код :', '', placeholder='ваш код',
                                                 max_chars=4,
                                                 type="password")
                    if st.session_state.card_no[4:7] in ['584']:
                        col3_text = 'Карта получателя'
                        col3_placeholder = '16 цифр'
                    else: 
                        col3_text = 'Карта получателя или номер магазина' 
                        col3_placeholder = '16 или 5 цифр'
                    card_to = col3.text_input(col3_text, '', placeholder=col3_placeholder,
                                                 max_chars=16,
                                                 type="password")
                    
                    pressed_minus = col4.form_submit_button("Подтвердить")
                    

                    if pressed_minus:
                        if st.session_state.card_no[4:7] in ['584']:
                            condition = verif_code == str(df["code"][0]) and card_to in [i.split("_")[0] for i in USERS.split(",")] and verif_code_2 == st.secrets['VER2'][st.session_state.card_no]
                        else:
                            if len(card_to)==5:
                                card_to = 11*"0" + card_to
                            condition = verif_code == str(df["code"][0]) and card_to in [i.split("_")[0] for i in USERS.split(",")]

                        if condition:
                            if card_to != st.session_state.card_no:
                                if df["balance"][0]>=balance_minus:
                                    
                                    # Проверка на совпадение валют
                                    df1 = conn.query('SELECT currency FROM cards WHERE card_no = :card_to;', 
                                                    show_spinner="Настройка безопасного соединения...",
                                                    ttl=0,#None, #"10m",
                                                    params={"card_to": card_to},)
                                    
                                    if df['currency'][0] == df1['currency'][0]:

                                        with conn.session as s1:
                                            # s1.execute(text(f'''UPDATE cards SET balance = balance - {str(balance_minus)} WHERE card_no = :card_no;
                                            #                 UPDATE cards SET balance = balance + {str(balance_minus)} WHERE card_no = :card_to;
                                            #                 '''), 
                                            # #ttl="10m",
                                            # params={"card_no": st.session_state.card_no, "card_to": card_to},)
                                            s1.execute(text(f'UPDATE cards SET balance = balance - {str(balance_minus)} WHERE card_no = :card_no;'), 
                                                    #ttl="10m",
                                                    params={"card_no": st.session_state.card_no},)
                                            s1.execute(text(f'UPDATE cards SET balance = balance + {str(balance_minus)} WHERE card_no = :card_to;'), 
                                                    #ttl="10m",
                                                    params={"card_to": card_to},)
                                        
                                            s1.commit()

                                        #st.success("Успешно. Если баланс не обновился, попробуйте скрыть-показать его с помощью ползунка 'Показать/скрыть баланс'.")
                                        success_transfer_classic(card_to, balance_minus, df['currency'][0])
                                    else:
                                        st.write(f"Карты имеют разные валюты. Невозможно конвертировать {df['currency'][0]} в {df1['currency'][0]}")
                                else:
                                    st.write("Недостаточно средств")
                            else:
                                st.write("Вы пытаетесь перевести самому себе. Перепроверьте номер карты получателя")
                        else:
                            st.write("Вы ввели неверный код или карта получателя или магазин с таким номером не существует")

        elif selection == "Обменять бонусы":
            with st.form("bonus_form", enter_to_submit=False):
                col0, col1 = st.columns([1, 4], gap="small", vertical_alignment="bottom")

                bonus_minus = col0.number_input('Введите кол-во бонусов для обмена :', value=None, placeholder='',
                                            step=1,
                                            min_value=1,
                                            max_value=1000)

                options_list =  BONUS_OPTIONS
                selected_option = col1.selectbox('Обменять на', options_list)
            
                col2, col3 = st.columns([3, 1], gap="small", vertical_alignment="bottom")

                verif_code = col2.text_input('Введите ваш смешарик-код :', '', placeholder='ваш код',
                                            max_chars=4,
                                            type="password")
                pressed_get_coupon = col3.form_submit_button("Подтвердить")

                if pressed_get_coupon:
                    if verif_code == str(df["code"][0]):
                        if df["cents_1"][0]>=bonus_minus:
                            with conn.session as s1:
                                s1.execute(text(f'UPDATE cards SET cents_1 = cents_1 - {str(bonus_minus)} WHERE card_no = :card_no;'), 
                                        #ttl="10m",
                                        params={"card_no": st.session_state.card_no},)
                            
                                s1.commit()

                                coupon_image_name = "coupon.png"
                                image_bytes = l_1(coupon_image_name.split('.')[0], f"{coupon_image_name.split('.')[0]}.txt")
                                # giant_str_coupon = st.secrets["pics"][coupon_image_name.split(".")[0]]
                                #im_coupon = Image.open(io.BytesIO(base64.decodebytes(bytes(giant_str_coupon, "utf-8"))))
                                #im_coupon = Image.open(io.BytesIO(base64.decodebytes(image_bytes)))
                                #im_coupon = Image.open(image_bytes)
                                im_coupon = Image.open(io.BytesIO(image_bytes))

                                draw_coupon = ImageDraw.Draw(im_coupon)
                                font_coupon = ImageFont.truetype("_helveticaneueui.ttf", 90)
                                font_coupon2 = ImageFont.truetype("_helveticaneueui.ttf", 55)
                                draw_coupon.text((200, 150), f"{(datetime.now() + timedelta(hours=st.secrets['tzs']['hours_to_local'])).strftime('%d.%m.%Y %H:%M:%S')}",font=font_coupon, fill=(78,51,46))

                                draw_coupon.text((150, 250), f"Кол-во: {bonus_minus}",font=font_coupon, fill=(78,51,46))

                                draw_coupon.text((150, 350), f"Вид бонуса:",font=font_coupon, fill=(78,51,46))

                                draw_coupon.text((150, 450), f"{selected_option}",font=font_coupon2, fill=(78,51,46))

                                draw_coupon.text((340, 500), f"Номер купона: {random.randint(10000,99999)}",font=font_coupon, fill=(78,51,46))

                                st.image(np.array(im_coupon), width=500)
                                st.success("""Успешно обменяли бонусы.  \nНЕ ЗАБУДЬТЕ СФОТОГРАФИРОВАТЬ ваш купон ,  \nтак как мы не храним данные о переводах""")

                        else:
                            st.write("Недостаточно бонусов")
                    else:
                        st.write("Неверный код")

        #elif selection == "Пополнить счёт": 

        elif selection == "Перевести между своими счетами" or selection == "Оплатить/Перевести валюту":   

            if selection == "Перевести между своими счетами":
                card_to = st.session_state.card_no
                user_selected = True
            else:
                with st.form("second_user_form", enter_to_submit=False):
                    col1, col2, = st.columns([3, 1], gap="small", vertical_alignment="bottom")
                    card_to = col1.text_input('Карта получателя или номер магазина', '', placeholder='16 или 5 цифр',
                                                    max_chars=16,
                                                    type="password")
                    user_selected = col2.form_submit_button("Подтвердить")

            if selection == "Оплатить/Перевести валюту":
                condition2 = card_to in [i.split("_")[0] for i in USERS.split(",")] and card_to != st.session_state.card_no
                left_header = 'Валюта отправителя'
                right_header = 'Валюта получателя'
            else: #"Перевести между своими счетами"
                condition2 = True
                left_header = 'Со счёта в'
                right_header = 'На счёт в'

            if condition2: # and user_selected:
                if card_to[4:7] in ['253', '111']:
                    
                    curs_1 =  [df["currency"][0], df["currency_2"][0] , df["currency_3"][0]]

                    if selection == "Оплатить/Перевести валюту":
                        df2 = conn.query('SELECT * FROM cards WHERE card_no = :card_to;', 
                                        show_spinner="Настройка безопасного соединения...",
                                        ttl=0,#None, #"10m",
                                        params={"card_to": card_to},)

                        curs_2 =  [df2["currency"][0], df2["currency_2"][0] , df2["currency_3"][0]]
                    else:
                        curs_2 = curs_1
                        df2 = df

                    if 'from_currency' not in st.session_state:
                        st.session_state.from_currency = curs_1[0]
                    if 'to_currency' not in st.session_state:
                        st.session_state.to_currency = curs_2[0]
                    if 'amount_from' not in st.session_state:
                        st.session_state.amount_from = 1.00
                    if 'amount_to' not in st.session_state:
                        st.session_state.amount_to = convert_currency(
                            st.session_state.amount_from,
                            st.session_state.from_currency,
                            st.session_state.to_currency
                        )

                    @st.fragment
                    def convertation_expander():
                        with st.expander("Детали конвертации", expanded=True):

                            col1, col2 = st.columns(2)

                            with col1:
                                cur1 = st.selectbox(
                                    left_header,
                                    options=curs_1,
                                    key='from_currency',
                                    on_change=on_from_currency_change
                                )
                            with col2:
                                cur2 = st.selectbox(
                                    right_header,
                                    options=curs_2,
                                    key='to_currency',
                                    on_change=on_to_currency_change
                                )

                            with col1:
                                am1 = st.number_input(
                                    label=f"Сумма в {st.session_state.from_currency}",
                                    #min_value=1,
                                    #step=0.01,
                                    value=st.session_state.amount_from,  #важно!!!
                                    format="%.2f",
                                    key='amount_from',
                                    on_change=on_amount_from_change
                                )
                            with col2:
                                am2 = st.number_input(
                                    label=f"Сумма в {st.session_state.to_currency}",
                                    value=convert_currency(am1, cur1, cur2),#1.00,
                                    #min_value=1,
                                    #step=0.01,
                                    format="%.2f",
                                    key='amount_to',
                                    on_change=on_amount_to_change
                                )
                            with col2:
                                verif_code =  st.text_input('Введите ваш смешарик-код :', '', placeholder='ваш код',
                                                    max_chars=4,
                                                    type="password")
                            losses = am1-convert_currency_real(am2, cur2, cur1)
                            st.caption(f"Ваши потери составляют : {am1:.2f}-{convert_currency_real(am2, cur2, cur1)}={losses} {cur1}")
                            if losses==0:
                                st.caption(":green[Отлично. Переведём без потерь]")
                            else:
                                st.caption("Мы не взимаем комиссию и не возьмём эти деньги , они не достанутся ни вам , ни нам , ни получателю. Чтобы избежать потерь старайтесь выбирать переводы в целых числах")

                            st.caption("Курсы для справки:")
                            st.caption(f"1 {cur1} = {convert_currency_real(1, cur1, cur2)} {cur2}")
                            st.caption(f"{convert_currency_real(1, cur2, cur1)} {cur1} = 1 {cur2}")

                            return cur1, cur2, am1, am2, verif_code

                    cur1, cur2, am1, am2, verif_code = convertation_expander()
                    if st.button('Выполнить перевод'):
                        total_1 = df["balance"][0]+df["cents_1"][0]/100
                        total_2 = df["second_balance"][0]+df["cents_2"][0]/100
                        total_3 = df["third_balance"][0]+df["cents_3"][0]/100

                        # total_4 = df2["balance"][0]+df2["cents_1"][0]/100
                        # total_5 = df2["second_balance"][0]+df2["cents_2"][0]/100
                        # total_6 = df2["third_balance"][0]+df2["cents_3"][0]/100

                        if selection == "Перевести между своими счетами" and st.session_state.from_currency == st.session_state.to_currency:
                            st.write("Нет смысла переводить между одним и тем же счётом. Выберите разные валюты")  
                        elif verif_code != str(df["code"][0]):
                            st.write("Неверный смешарик-код")
                        else:
                            if cur1==curs_1[0] and verif_code == str(df["code"][0]):
                                if am1 > total_1:
                                    st.write("Недостаточно средств на счёте")
                                else:
                                    new_balance_int, new_balance_cents = int_float_calc(df["balance"][0],df["cents_1"][0], -am1)
                                    #Списание пользователя1
                                    upd("balance", "cents_1",  new_balance_int, new_balance_cents, st.session_state.card_no)

                                    if cur2==curs_2[0]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["balance"][0],df2["cents_1"][0], am2)
                                        #Пополнение пользователя2
                                        upd("balance", "cents_1", new_balance2_int, new_balance2_cents, card_to)
                            
                                    elif cur2==curs_2[1]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["second_balance"][0],df2["cents_2"][0], am2)
                                        #Пополнение пользователя2
                                        upd("second_balance", "cents_2", new_balance2_int, new_balance2_cents, card_to)

                                    elif cur2==curs_2[2]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["third_balance"][0],df2["cents_3"][0], am2)
                                        #Пополнение пользователя2
                                        upd("third_balance", "cents_3", new_balance2_int, new_balance2_cents, card_to)
                                    
                                    success_transfer(card_to, selection)

                            elif cur1==curs_1[1] and verif_code == str(df["code"][0]):
                                if am1 > total_2:
                                    st.write("Недостаточно средств на счёте")
                                else:
                                    new_balance_int, new_balance_cents = int_float_calc(df["second_balance"][0],df["cents_2"][0], -am1)
                                    #Списание пользователя1
                                    upd("second_balance", "cents_2",  new_balance_int, new_balance_cents, st.session_state.card_no)        
                                
                                    if cur2==curs_2[0]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["balance"][0],df2["cents_1"][0], am2)
                                        #Пополнение пользователя2
                                        upd("balance", "cents_1", new_balance2_int, new_balance2_cents, card_to)
                            
                                    elif cur2==curs_2[1]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["second_balance"][0],df2["cents_2"][0], am2)
                                        #Пополнение пользователя2
                                        upd("second_balance", "cents_2", new_balance2_int, new_balance2_cents, card_to)

                                    elif cur2==curs_2[2]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["third_balance"][0],df2["cents_3"][0], am2)
                                        #Пополнение пользователя2
                                        upd("third_balance", "cents_3", new_balance2_int, new_balance2_cents, card_to)
                                    
                                    success_transfer(card_to, selection)

                            elif cur1==curs_1[2] and verif_code == str(df["code"][0]):
                                if am1 > total_3:
                                    st.write("Недостаточно средств на счёте")
                                else:
                                    new_balance_int, new_balance_cents = int_float_calc(df["third_balance"][0],df["cents_3"][0], -am1)
                                    #Списание пользователя1
                                    upd("third_balance", "cents_3",  new_balance_int, new_balance_cents, st.session_state.card_no)        
                                    
                                    if cur2==curs_2[0]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["balance"][0],df2["cents_1"][0], am2)
                                        #Пополнение пользователя2
                                        upd("balance", "cents_1", new_balance2_int, new_balance2_cents, card_to)
                            
                                    elif cur2==curs_2[1]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["second_balance"][0],df2["cents_2"][0], am2)
                                        #Пополнение пользователя2
                                        upd("second_balance", "cents_2", new_balance2_int, new_balance2_cents, card_to)

                                    elif cur2==curs_2[2]:
                                        new_balance2_int, new_balance2_cents = int_float_calc(df2["third_balance"][0],df2["cents_3"][0], am2)
                                        #Пополнение пользователя2
                                        upd("third_balance", "cents_3", new_balance2_int, new_balance2_cents, card_to)

                                    success_transfer(card_to, selection)

                else:
                    st.write(f"Карты имеют разные типы. Невозможно конвертировать")
            elif card_to == st.session_state.card_no and selection == "Оплатить/Перевести валюту":
                st.write("Для перевода самому себе воспользуйтесь соседней вкладкой 'Между своими счетами'")
            elif card_to is not None and card_to!="":
                st.write("Карта получателя или магазин с таким номером не существует")

        elif selection == "Посмотреть курсы валют":
            @st.fragment
            def cur_info():
                every_cur = [f'{i}, {st.secrets.cur[i]["forms"][4]}' for i in RATES.keys()]

                option = st.selectbox(
                    "Показать",
                    ["Все пары валют", "Мои валюты в переводе на другие валюты", 
                    "Другие валюты в переводе на мои валюты"] + every_cur,
                )

                if option == "Все пары валют":
                    curs_left = RATES.keys()
                    curs_right = RATES.keys()
                elif option =="Мои валюты в переводе на другие валюты":
                    curs_left = [df["currency"][0], df["currency_2"][0] , df["currency_3"][0]]
                    curs_right = RATES.keys()
                elif option =="Другие валюты в переводе на мои валюты":
                    curs_left = RATES.keys() 
                    curs_right = [df["currency"][0], df["currency_2"][0] , df["currency_3"][0]]
                else:
                    curs_left = [option[:3]]
                    curs_right = RATES.keys()

                # for from_cur, rate_from in RATES.items():
                #     for to_cur, rate_to in RATES.items():
                for from_cur in curs_left:
                    st.subheader(f"{from_cur}")
                    st.caption(f"{st.secrets.cur[from_cur]['forms'][4]}")
                    cur_col1, cur_col2, = st.columns([1, 1])
                    with cur_col1:
                        st.text(f"Прямой курс")
                        for to_cur in curs_right:
                    
                            if from_cur == to_cur:
                                continue
                            rate_from = RATES[from_cur]
                            rate_to = RATES[to_cur]

                            # Складываем пример: 1 USD = x EUR
                            x = 1
                            # Конвертируем 1 unit from_cur в to_cur по курсу
                            y = round(rate_to / rate_from, 4)
                            st.metric(label="", value =f"{x} {from_cur} = {y} {to_cur}")
                    with cur_col2:
                        st.text(f"Обратный курс")
                        for to_cur in curs_right:
                    
                            if from_cur == to_cur:
                                continue
                            rate_from = RATES[from_cur]
                            rate_to = RATES[to_cur]

                            # Складываем пример: 1 USD = x EUR
                            x = 1
                            # Конвертируем 1 unit from_cur в to_cur по курсу
                            y = round(rate_from / rate_to, 4)
                            st.metric(label="", value =f"{x} {to_cur} = {y} {from_cur}")

                    st.divider()

            cur_info()

        if st.button("Выйти"):
            st.session_state.card_no = None
            st.session_state.code = None
            #st.empty()
            st.session_state.logged_in = False
            empty()
            st.rerun()
