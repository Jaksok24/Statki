import sqlite3
from datetime import date as day
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import logging
from logging import getLogger
import re
import os

# Konfiguracja strony
st.set_page_config(page_title="Statki", page_icon=":ship:", layout="wide")

app_logger = getLogger()
app_logger.addHandler(logging.StreamHandler())
app_logger.setLevel(logging.INFO)

#Style
title_style = "color: White; background-color: #B0C4DE; text-align: Center; border-radius: 10px;"
info_style = "color: White; background-color: #87CEFA; text-align: Center; border-radius: 10px; font-weight: bold;"

#Łączenia się z bazą danych
conn = sqlite3.connect("statki.db")
c = conn.cursor()
# c.execute('''CREATE TABLE IF NOT EXISTS rejs (id INTEGER PRIMARY KEY, customer TEXT, date DATE, hour TIME, ship TEXT, fee BOOLEAN, people INTEGER, nb TEXT, cruise TEXT, fee_cost INTEGER, catering TEXT, note TEXT, dc TEXT, checked TEXT)''')
# c.execute('''CREATE TABLE IF NOT EXISTS dinners (dID INTEGER PRIMARY KEY, dinner TEXT, data DATE, hour_start TIME, hour_stop TIME, people INEGER, checked TEXT)''')

#Tablice/zmienne wykorzystywane dla całej aplikacji
current_time = datetime.now().strftime("%H:%M")
today = day.today()
albatros = []
biala_mewa = []
kormoran = []
ckt_vip = []
tablicaDanych = []
tablicaDanych2 = []
editData = []
test = []

#Klasa szczegółowych danych o statkach
class Details:
    def __init__(self, id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note, check):
        self.id = id
        self.customer = customer
        self.dc = dc
        self.nb = nb
        self.date = date
        self.hour = hour
        self.cruise = cruise
        self.ship = ship
        self.people = people
        self.fee = fee
        self.fee_cost = fee_cost
        self.catering = catering
        self.note = note
        self.check = check
        
    def printData(self):
        data = [f"Imię i nazwisko: {self.customer}", f"Numer telefonu: {self.dc} {self.nb}", f"Data rejsu: {self.date}", f"Godzina: {self.hour}", self.cruise, f"Liczba ludzi: {self.people}", f"Zaliczka: {self.fee}", f"Kwota zaliczki: {self.fee_cost} PLN", f"Katering: {self.catering}", f"Notatki: {self.note}"]
        return data

#Klasa rejsów do strony głównej
class Cruise:
    def __init__(self, id, hour, people, ship, cruise, catering, check, date):
        self.id = id
        self.hour = hour
        self.people = people
        self.ship = ship
        self.cruise = cruise
        self.catering = catering
        self.check = check
        self.date = date

#Klasa do informacji o obiadach
class Dinner:
    def __init__(self, dID, hour_start, hour_stop, group, name, empty1, check, date):
        self.dID = dID
        self.hour_start = hour_start
        self.hour_stop = hour_stop
        self.group = group
        self.name = name
        self.empty1 = empty1
        self.check = check
        self.date = date

class Cruise2:
    def __init__(self, cID, name, times):
        self.cID = cID
        self.name = name
        self.times = times

#Funkcja dodająca przewidywany czas powrotu
def timeCruise(elem):
    global new_time
    time = datetime.strptime(elem.hour, '%H:%M')
    pattern = r"(\d{2}):(\d{2})h"
    match = re.search(pattern, elem.cruise)
    godz, min = match.groups()
    new_time = time + timedelta(hours=int(godz), minutes=int(min))
    return new_time

#Wybierz dzień
def choiceTheDay():
    columns = st.columns([1,1,1,1])
    with columns[0]:
        theDay = st.date_input("Wybierz dzień")
    return theDay

#Pobieranie spisu wszystkich aktywności w danym dniu z bazy danych
def getShortData(theDay):
    c.execute(f'''SELECT * FROM
              (SELECT id, hour, SUM(people), ship, cruise, catering, checked, date FROM rejs GROUP BY hour, ship, cruise
              UNION
              SELECT dID, hour_start as hour, hour_stop, people, dinner, ' ', checked, data as date FROM dinners)
              WHERE date='{theDay}' ORDER BY hour''')
    for elem in c.fetchall():
        if elem[6] == 'cruise':
            cruiseInfo = Cruise(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6], elem[7])
            tablicaDanych.append(cruiseInfo)
        else:
            dinnerInfo = Dinner(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6], elem[7])
            tablicaDanych.append(dinnerInfo)
            
#Wyświetl skrócone dane o rejsie na dany dzień
def printData(): 
    st.markdown('''<table style="border: 0; border-collapse: collapse; border: 0; text-align: Center; width: 100%;">
                <tr style="border: 0;">
                <td style="border: 0; width: 20%"><h3>Godzina</h3></td>
                <td style="border: 0; width: 20%"><h3>Rejs</h3></td>
                <td style="border: 0; width: 20%;"><h3>Osoby</h3></td>
                <td style="border: 0; width: 20%;"><h3>Statek</h3></td>
                <td style="border: 0; width: 20%;"><h3>Catering</h3>
                </td></tr></table><br>''', unsafe_allow_html=True)
    for elem in tablicaDanych:  
        if elem.check == 'cruise':
            timeCruise(elem)
            time_str2 = new_time.strftime('%H:%M')
            st.markdown(f'''<table style="border-collapse: collapse; border: 0; border-radius: 12px; text-align: Center; width: 100%; background-color: #87CEFA; color: Black;">
                        <tr style="border: 0;">
                        <td style="width: 20%; border: 0;">{elem.hour} - {time_str2}</td>
                        <td style="width: 20%; border: 0;">{elem.cruise}</td>
                        <td style="width: 20%; border: 0;">{elem.people} osób</td>
                        <td style="width: 20%; border: 0;">{elem.ship}</td>
                        <td style="width: 20%; border: 0;">{elem.catering}</td>
                        </tr></table><br>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''<table style="border-collapse: collapse; border: 0; border-radius: 12px; text-align: Center; width: 100%; background-color: #FFDEAD; color: Black;">
                        <tr style="border: 0;">
                        <td style="width: 20%; border: 0;">{elem.hour_start} - {elem.hour_stop}</td>
                        <td style="width: 20%; border: 0;"></td>
                        <td style="width: 20%; border: 0;">{elem.group} osób</td>
                        <td style="width: 20%; border: 0;"></td>
                        <td style="width: 20%; border: 0;">{elem.name}</td>
                        </tr></table><br>''', unsafe_allow_html=True)

#Pobieranie z bazy danych skróconych informacji o wszystkich rejsach
def getShortDataForAll():
    c.execute('''SELECT id, hour, SUM(people), ship, cruise, catering, checked, date FROM rejs GROUP BY hour, ship, cruise ORDER BY date, hour''')
    for elem in c.fetchall():
        cruiseInfo = Cruise(elem[0], elem[1], elem[2], elem[3], elem[4], elem[5], elem[6], elem[7])
        tablicaDanych2.append(cruiseInfo)

#Funkcja do wyświetlania skróconych danych o rejsach dla wszystkich dni
def printDataForAll():
    st.markdown('''<table style="border: 0; border-collapse: collapse; border: 0; text-align: Center; width: 100%;">
                <tr style="border: 0;">
                <td style="border: 0; width: 16%"><h3>Data</h3></td>
                <td style="border: 0; width: 16%"><h3>Godzina</h3></td>
                <td style="border: 0; width: 16%"><h3>Rejs</h3></td>
                <td style="border: 0; width: 16%;"><h3>Osoby</h3></td>
                <td style="border: 0; width: 16%;"><h3>Statek</h3></td>
                <td style="border: 0; width: 16%;"><h3>Catering</h3>
                </td></tr></table><br>''', unsafe_allow_html=True)
    for elem in tablicaDanych2:
        timeCruise(elem)
        time_str3 = new_time.strftime('%H:%M')
        st.markdown(f'''<table style="border-collapse: collapse; border: 0; border-radius: 12px; text-align: Center; width: 100%; background-color: #87CEFA; color: Black;">
                        <tr style="border: 0;">
                        <td style="width: 16%; border: 0">{elem.date}</td>
                        <td style="width: 16%; border: 0;">{elem.hour} - {time_str3}</td>
                        <td style="width: 16%; border: 0">{elem.cruise}</td>
                        <td style="width: 16%; border: 0">{elem.people} osób</td>
                        <td style="width: 16%; border: 0">{elem.ship}</td>
                        <td style="width: 16%; border: 0">{elem.catering}</td>
                        </tr></table><br>''', unsafe_allow_html=True)

#Zapisywanie danych do poszczególnych tablic
def saveDataToArray():
    c.execute(f"SELECT id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note, checked FROM rejs WHERE date='{theDay2}' ORDER BY hour")
    for row in c.fetchall():
        cruiseInfo = Details(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
        if cruiseInfo.ship == "Albatros":
            albatros.append(cruiseInfo)
        if cruiseInfo.ship == "Biała Mewa":
            biala_mewa.append(cruiseInfo)
        if cruiseInfo.ship == "Kormoran":
            kormoran.append(cruiseInfo)
        if cruiseInfo.ship == "CKT VIP":
            ckt_vip.append(cruiseInfo)
    
#Wyświetlanie szczegółowych informacji o rejsach
def showDetails(shipTable):
    for i, object in enumerate(shipTable):
        timeCruise(object)
        time_str = new_time.strftime('%H:%M')
        st.markdown(f"<p style=\"{info_style}\">{object.hour} - {time_str}<br>{object.cruise}<br>Ilość osób: {object.people}<p>", unsafe_allow_html=True)
        with st.expander("Szczegóły"):
            for info in object.printData():
                st.write(info)

#Dodawanie nazw rejsów
def UpdateCruisesNames():
    rejsy = []
    c.execute("SELECT rID, name, times FROM rejsy;")
    for elem in c.fetchall():
        cruiseInfo = Cruise2(elem[0] ,elem[1], elem[2])
        cruiseInfo2 = cruiseInfo.name + ' - ' + str(cruiseInfo.times) + "h"
        rejsy.append(cruiseInfo2)
    return rejsy

#Dodawanie informacji o rejsie
def addCruiseInfo():
    rejsy = UpdateCruisesNames()
    with st.container(border=True):
        columns = st.columns([1,1])
        with columns[0]:
            customer = st.text_input("Podaj imię i nazwisko")
            date = st.date_input("Podaj dzień", value=today, format="DD.MM.YYYY", label_visibility="visible")
            ship = st.selectbox("Wybierz statek", ["Albatros", "Biała Mewa", "Kormoran", "CKT VIP", ""])
            fee = st.selectbox("Zaliczka", ["Nie", "Tak"])
            people = st.number_input("Ilość osób", step=1, max_value=60, min_value=0) if ship == "Albatros" else st.number_input("Ilość osób", step=1, max_value=30, min_value=0)
        with columns[1]:
            phone_column = st.columns([1,3])
            with phone_column[0]:
                dc = st.selectbox("Kierunkowy", ["🇵🇱 +48", "🇷🇺 +7", "🇩🇪 +49", "🇱🇹 +370", "🇱🇻 +371", "🇪🇪 +372", "🇺🇦 +380", "🇨🇿 +420", "🇸🇰 +421"])
            with phone_column[1]:
                nb = st.text_input("Podaj numer telefonu")
            hour = st.time_input("Podaj godzinę")
            cruise = st.selectbox("Wybierz rejs", rejsy)
            fee_cost = st.number_input("Kwota zaliczki")
            catering = st.selectbox("Katering", ["Nie", "Tak"])
        note = st.text_area("Notatki")
        add_button = st.button("Zapisz")
    if add_button:
        if customer != "" and nb != "":
            hour_str = hour.strftime("%H:%M")
            try:
                c.execute("INSERT INTO rejs (customer, date, hour, ship, fee, people, nb, cruise, fee_cost, catering, note, dc, checked) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'cruise')",
                        (customer, date, hour_str, ship, fee, people, nb, cruise, fee_cost, catering, note, dc))
                conn.commit()
                st.success("Dane zostały dodane pomyślnie")
            except sqlite3.Error as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Wprowadź dane", icon="🚨")
            
#Dodawanie informacji o obiadach
def addDinner():
    with st.container(border=True):
        dinner = st.text_area("Podaj obiad", key="dinner_add1")
        group = st.number_input("Podaj liczbę osób", min_value=0, step=1, key="dinner_add2")
        dinCol = st.columns([1,1])
        with dinCol[0]:
            date = st.date_input("Podaj date", key="dinner_add3")
        with dinCol[1]:
            dinCol2 = st.columns([1,1])
            with dinCol2[0]:
                hour_start = st.time_input("Podaj godzinę rozpoczęcia", key="dinner_add4")
            with dinCol2[1]:
                hour_stop = st.time_input("Podaj godzinę zakończenia", key="dinner_add4+1")
        dinBut = st.button("Dodaj obiad")
        if dinBut:
            if dinner != "":
                hour_str = hour_start.strftime("%H:%M")
                hour_str2 = hour_stop.strftime("%H:%M")
                try:
                    c.execute('''INSERT INTO dinners (dinner, data, hour_start, hour_stop, people, checked) VALUES (?,?,?,?,?, 'dinner')''', (dinner, date, hour_str, hour_str2, group))
                    conn.commit()
                    st.success("Dodano obiad")
                except sqlite3.Error as e:
                    st.error(f"An error occurred: {e}")

def addCruise():
    st.markdown("<h2>Dodaj rejs</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        acc = st.columns([1,1])
        with acc[0]:
            name = st.text_input("Podaj nazwę rejsu")
        with acc[1]:
            times = st.time_input("Podaj czas trwania", value=None)
        addCruiseButton = st.button("Dodaj")
        if addCruiseButton:
            if name != "" and times != "":
                times_str = times.strftime("%H:%M")
                c.execute("SELECT name FROM rejsy")
                for elem in c.fetchall():
                    if elem[0] != name:
                        checked = 1
                    else:
                        st.warning("Taki rejs już istnieje", icon="⚠️")
                if checked == 1:
                    c.execute('''INSERT INTO rejsy (name, times) VALUES (?, ?)''', (name, times_str))
                    conn.commit()
            else:
                st.warning("Wprowadź dane", icon="⚠️")
            
    cruiseTb = []
    c.execute("SELECT rID, name, times FROM rejsy")
    for elem in c.fetchall():
        cruiseNames = Cruise2(elem[0], elem[1], elem[2])
        cruiseTb.append(cruiseNames)
    
    st.divider()
    st.markdown("<h2>Edytuj wpisane rejsy</h2>", unsafe_allow_html=True)
    for i, elem in enumerate(cruiseTb):
        with st.popover(f"{elem.name} | {elem.times}h", use_container_width=True):
            editCruise(i, elem)

def editCruise(i, obj):
    acc = st.columns([1,1])
    new_time = datetime.strptime(obj.times, "%H:%M")
    with acc[0]:
        name = st.text_input("Podaj nazwę rejsu", value=obj.name, key=f"aaa{i}")
    with acc[1]:
        times = st.time_input("Podaj czas trwania", value=new_time, key=f"bbb{i}")
    ecc = st.columns([1,1,1,1,1,1])
    with ecc[0]:
        deleteCruiseButton = st.button("Usuń", key=f"ddd{i}")
    with ecc[5]:
        acceptCruiseButton = st.button("Zapisz zmiany", key=f"ccc{i}")
    if deleteCruiseButton:
        c.execute(f"DELETE FROM rejsy WHERE rID = {obj.cID}")
        conn.commit()
        st.success(f"Usunięto dane")
    if acceptCruiseButton:
        times_str = times.strftime("%H:%M")
        c.execute(f"UPDATE rejsy SET name = ?, times = ? WHERE rID={obj.cID}", (name, times_str))
        conn.commit()
        st.success("Zapisano dane")

#Edytowanie danych
def editInfo():
    c.execute('''SELECT * FROM
              (SELECT id, customer, dc, nb, date, hour, cruise, ship, people, fee, fee_cost, catering, note, checked FROM rejs
              UNION
              SELECT dID, hour_start as hour, hour_stop, people, dinner, ' ', ' ', data as date, ' ', ' ', ' ', ' ', ' ', checked FROM dinners)
              ORDER BY hour, date''')
    for row in c.fetchall():
        if row[13] == 'cruise':
            cruiseInfo = Details(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], int(row[8]), row[9], row[10], row[11], row[12], row[13])
            editData.append(cruiseInfo)
        else:
            dinnerInfo = Dinner(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            editData.append(dinnerInfo)
    for i, elem in enumerate(editData):
        if elem.check == 'cruise':
            st.write(f"Rejs nr {elem.id}")
            with st.popover(f"{elem.customer} | {elem.ship} | {elem.cruise} | {elem.date} | {elem.hour}", use_container_width=True):
                editCruiseInfo(i, elem)
        else:
            st.write(f"Obiad nr {elem.dID}")
            with st.popover(f"{elem.name} | {elem.date} | {elem.hour_start} - {elem.hour_stop}", use_container_width=True):
                editDinnerInfo(i, elem)

#Inputy pobierające dane z rekordów tabeli
def editCruiseInfo(i, obj):
    rejsy = UpdateCruisesNames()
    columns = st.columns([1,1])
    with columns[0]:
        customer = st.text_input("Imię i nazwisko", value=obj.customer, key=f"a{i}")
        date = st.date_input("Dzień", value=datetime.strptime(obj.date, "%Y-%m-%d").date(), format="DD.MM.YYYY", min_value=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), key=f"b{i}")
        ship = st.selectbox("Statek", ["Albatros", "Biała Mewa", "Kormoran", "CKT VIP"], index=["Albatros", "Biała Mewa", "Kormoran", "CKT VIP", None].index(obj.ship), key=f"c{i}")
        fee = st.selectbox("Zaliczka", ["Nie", "Tak"], index=["Nie", "Tak"].index(obj.fee), key=f"d{i}")
        people = st.number_input("Ilość osób", step=1, max_value=60, min_value=0, value=obj.people, key=f"e{i}")
    with columns[1]:
        phone_column = st.columns([1,3])
        with phone_column[0]:
            dc = st.selectbox("Kierunkowy", ["🇵🇱 +48", "🇷🇺 +7", "🇩🇪 +49", "🇱🇹 +370", "🇱🇻 +371", "🇪🇪 +372", "🇺🇦 +380", "🇨🇿 +420", "🇸🇰 +421"], index=["🇵🇱 +48", "🇷🇺 +7", "🇩🇪 +49", "🇱🇹 +370", "🇱🇻 +371", "🇪🇪 +372", "🇺🇦 +380", "🇨🇿 +420", "🇸🇰 +421"].index(obj.dc), key=f"f{i}")
        with phone_column[1]:
            nb = st.text_input("Numer telefonu", value=obj.nb, key=f"g{i}")
        hour = st.time_input("Godzina", value=datetime.strptime(obj.hour, '%H:%M').time(), key=f"h{i}")
        cruise = st.selectbox("Rejs", [row for row in rejsy], index=obj.cruise.index(obj.cruise), key=f"i{i}")
        fee_cost = st.number_input("Kwota zaliczki", value=obj.fee_cost, key=f"j{i}")
        catering = st.selectbox("Katering", ["Nie", "Tak"], index=["Nie", "Tak"].index(obj.catering), key=f"k{i}")
    note = st.text_area("Notatki", value=obj.note, key=f"l{i}")
    cb = st.columns([1,1,1,1,1])
    with cb[0]:
        accept_changes_button = st.button("Zapisz zmiany", key=f"m{i}")
    with cb[4]:
        delete_button = st.button("Usuń", key=f"n{i}")
    if accept_changes_button:
        hour_str = hour.strftime("%H:%M")
        date_str = date.strftime("%Y-%m-%d")
        c.execute("UPDATE rejs SET customer = ?, dc = ?, nb = ?, date = ?, hour = ?, cruise = ?, ship = ?, people = ?, fee = ?, fee_cost = ?, catering = ?, note = ? WHERE id = ?",
            (customer, dc, nb, date_str, hour_str, cruise, ship, people, fee, fee_cost, catering, note, obj.id))
        conn.commit()
        st.success( "Zaktualizowano dane")
    if delete_button:
        c.execute(f"DELETE FROM rejs WHERE id = {obj.id}")
        conn.commit()
        st.success(f"Usunięto dane")

#dID, hour, group, name, empty1, empty2, check, date
def editDinnerInfo(i, obj):
    dinner = st.text_area("Podaj obiad", value=obj.name, key=f"dinner_a{i}")
    group = st.number_input("Podaj liczbę osób", min_value=0, step=1, value=obj.group, key=f"dinner_b{i}")
    dinCol = st.columns([1,1])
    with dinCol[0]:
        date = st.date_input("Podaj date", value=datetime.strptime(obj.date, "%Y-%m-%d").date(), format="DD.MM.YYYY", min_value=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), key=f"dinner_c{i}")
    with dinCol[1]:
        dinCol2 = st.columns([1,1])
        with dinCol2[0]:
            hour_start = st.time_input("Podaj godzinę rozpoczęcia", value=datetime.strptime(obj.hour_start, '%H:%M').time(), key=f"dinner_d{i}")
        with dinCol2[1]:
            hour_stop = st.time_input("Podaj godzinę zakończenia", value=datetime.strptime(obj.hour_stop, '%H:%M').time(), key=f"dinner_2d{i}")
    cb = st.columns([1,1,1,1,1])
    with cb[0]:
        accept_changes_button_dinner = st.button("Zapisz zmiany", key=f"m{i}")
    with cb[4]:
        delete_button_dinner = st.button("Usuń", key=f"n{i}")
    if accept_changes_button_dinner:
        hour_str = hour_start.strftime("%H:%M")
        hour_str2 = hour_stop.strftime("%H:%M")
        date_str = date.strftime("%Y-%m-%d")
        c.execute("UPDATE dinners SET dinner = ?, data = ?, hour_start = ?, hour_stop = ?, people = ? WHERE dID = ?", (dinner, date_str, hour_str, hour_str2, group, obj.dID))
        conn.commit()
        st.success( "Zaktualizowano dane")
    if delete_button_dinner:
            c.execute(f"DELETE FROM dinners WHERE dID = {obj.dID}")
            conn.commit()
            st.success("Usunięto dane")
 
#Ustawienia SideBar
with st.sidebar:
    selected = option_menu(
        menu_title = "Port Katamaranów",
        options = ["Strona główna", "Panel zarządzania", "Szczegóły", "Spis rejsów"],
        icons = ["house", "pencil-square", "book", "archive"],
        menu_icon="tsunami",
        default_index = 0,
    )

#Strona główna
if (selected == "Strona główna"):
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    st.write(f"Znalezione tabele: {tables}")
    
    tab_1, tab_2 = st.tabs(["WYBRANY DZIEŃ :sunrise:", "WSZYSTKO :scroll:"])
    with tab_1:
        theDay = choiceTheDay()
        getShortData(theDay)
        printData()
    with tab_2:
        getShortDataForAll()
        printDataForAll()

#Szczegóły rejsów
if (selected == "Szczegóły"):
    st.title("Szczegóły rejsów :ship:")

    theDay2 = choiceTheDay()
    saveDataToArray()

    #Wyświetl dane
    scr = st.columns([1,1,1,1])
    albatros_tab, biala_mewa_tab, kormoran_tab, ckt_vip_tab = st.tabs(["Albatros", "Biała mewa", "Kormoran", "CKT VIP"])
    with albatros_tab: 
        st.markdown(f"<h3 style=\"{title_style}\">Albatros<p>Limit osób: 60</p></h3>", unsafe_allow_html=True)
        st.divider()
        showDetails(albatros)
    with biala_mewa_tab:
        st.markdown(f"<h3 style=\"{title_style}\">Biała Mewa<p>Limit osób: 30</p></h3>", unsafe_allow_html=True)
        st.divider()
        showDetails(biala_mewa)
    with kormoran_tab:
        st.markdown(f"<h3 style=\"{title_style}\">Kormoran<p>Limit osób: 30</p></h3>", unsafe_allow_html=True)
        st.divider()
        showDetails(kormoran)
    with ckt_vip_tab:
        st.markdown(f"<h3 style=\"{title_style}\">CKT VIP<p>Limit osób: 30</p></h3>", unsafe_allow_html=True)
        st.divider()
        showDetails(ckt_vip)

#Panel zarządzania danymi
if selected == "Panel zarządzania":
    tab1, tab2, tab3, tab4 = st.tabs(["DODAJ REJS :anchor:", "DODAJ OBIAD :knife_fork_plate:", "EDYTUJ DANE :pencil:", "ZARZĄDZAJ REJSAMI :ship:"])
    with tab1:
        addCruiseInfo()
    with tab2:
        addDinner()
    with tab3:
        editInfo()
    with tab4:
        addCruise()

#Zapisz do DataFrame wszystkie dane z tabeli
def showAllData():
    c.execute("SELECT customer, dc, nb, ship, date, hour, cruise, people, fee, fee_cost, catering, note FROM rejs ORDER BY date, hour")
    df = pd.DataFrame([row for row in c.fetchall()], columns=("Imię i nazwisko", "Kierunkowy", "Nr tel", "Statek", "Data", "Godzina", "Rejs", "Ilość ludzi", "Zaliczka", "Kwota zaliczki", "Katering", "Notatki"))
    return df

#Filtrowanie
def Filtr(name, start, stop, search):
    if search:
        query = """SELECT customer, dc, nb, ship, date, hour, cruise, people, fee, fee_cost, catering, note
                   FROM rejs WHERE 1=1"""
        if name:
            query += f" AND (customer LIKE '%{name}%' OR ship LIKE '%{name}%' OR cruise LIKE '%{name}%' OR fee LIKE '%{name}%' OR people LIKE '%{name}%' OR nb LIKE '%{name}%' OR catering LIKE '%{name}%' OR note LIKE '%{name}%')"
        if start and stop:
            query += f" AND date BETWEEN '{start}' AND '{stop}'"
        query += " ORDER BY date, hour"
        c.execute(query)
        rows = c.fetchall()
        if rows:
            df = pd.DataFrame(rows, columns=("Imię i nazwisko", "Kierunkowy", "Nr tel", "Statek", "Data", "Godzina", "Rejs", "Ilość ludzi", "Zaliczka", "Kwota zaliczki", "Katering", "Notatki"))    
        else:
            df = pd.DataFrame(columns=("Imię i nazwisko", "Kierunkowy", "Nr tel", "Statek", "Data", "Godzina", "Rejs", "Ilość ludzi", "Zaliczka", "Kwota zaliczki", "Katering", "Notatki"))
        return df
    else:
        return showAllData()

#Historia
if (selected == "Spis rejsów"):
    st.markdown("<h1 style=\"background-color: #87CEFA; color: #FFFFFF; border-radius: 10px; font-weight: bold; padding-left: 1rem;\">Spis rejsów<h1>", unsafe_allow_html=True)
    with st.container(border=True):
        filcol = st.columns([1,1])
        with filcol[0]:
            filtr_input = st.text_input("Filtruj")
        with filcol[1]:
            filcol2 = st.columns([1,1])
            with filcol2[0]:
                start_time_filtr = st.date_input("Początek", value=None)
            with filcol2[1]:
                end_time_filtr = st.date_input("Koniec", value=None)
        bfiltr_col = st.columns([1,1,1,1,1])
        with bfiltr_col[0]:
            search_button = st.button("Szukaj")
        with bfiltr_col[4]:
            clear_button = st.button("Wyczyść filtry")
        if clear_button:
            dataframe_data = showAllData()
        elif search_button:
            dataframe_data = Filtr(filtr_input, start_time_filtr, end_time_filtr, search_button)
        else:
            dataframe_data = pd.DataFrame()
    dataframe_data = Filtr(filtr_input, start_time_filtr, end_time_filtr, search_button)
    st.dataframe(dataframe_data)

conn.close()
