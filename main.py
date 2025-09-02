#railway project using sqlite and streamlit python

#import packages and import database

import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect('railway.db')
current_page = 'Login or Sign up'
c = conn.cursor()


def create_db():
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT , password TEXT)")

    c.execute("CREATE TABLE IF NOT EXISTS employees (employee_id TEXT , password TEXT , designation TEXT)")

    c.execute(
        "CREATE TABLE IF NOT EXISTS trains (train_number TEXT , train_name TEXT , start_destination TEXT , end_destination TEXT)")

    create_db()


#Searchtrain:

def search_train(train_number):
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data = train_query.fetchall()

    return train_data


#train Destination search:

def train_destination(start_destination, end_destination):
    train_query = c.execute("SELECT * FROM trains WHERE start_destination=? AND end_destination=?",
                            (start_destination, end_destination))
    train_data = train_query.fetchone()

    return train_data


#add train

def add_train(train_number, train_name, departure_date, start_destination, end_destination):
    c.execute(
        "INSERT INTO trains (train_number, train_name, departure_date, start_destination, end_destination) values(?,?,?,?,?)",
        (train_number, train_name, departure_date, start_destination, end_destination))

    conn.commit()
    st.success("New train added")
    create_seat_table(train_number)


#create seat in train :

def create_seat_table(train_number):
    c.execute(f"CREATE TABLE IF NOT EXISTS seats_{train_number}"
              f"( seat_number INTEGER PRIMARY KEY,"
              f"seat_type TEXT,"
              f"booked INTEGER,"
              f"passenger_name TEXT,"
              f"passenger_age INTEGER,"
              f"passenger_gender TEXT,")

    for i in range(1, 51):
        val = categorize_seat(i)
        c.execute(
            f"INSERT INTO seats_{train_number}(seat_number, seat_type, booked, passenger_name, passenger_age, passenger_gender) values(?,?,?,?,?,?);",
            (i, val, 0, ''','''))

        conn.commit()


#allocate_next_available_seats:

def allocate_next_available_seat(train_number, seat_type):
    seat_query = c.execute(f"SELECT seat_number FROM seats_{train_number} WHERE booked=0 and seat_type=?"
                           f"ORDER by seat_number ASC", (seat_type,))

    result = seat_query.fetchall()

    if result:
        return [0]
    return None


#categorize_seats_trains:

def categorize_seat(seat_num):
    if (seat_num % 10) in [0, 4, 5, 9]:
        return "window"
    elif (seat_num % 10) in [2, 3, 6, 7]:
        return "Aisle"
    else:
        return "Middle"


#view_seats

def view_seats(train_number):
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data = train_query.fetchone()
    if train_data:
        seat_query = c.execute(
            f'''SELECT 'Number:' || seat_number, '\n Type:' || seat_type, '\n Name:' || passenger_name, '\n Age:'|| passenger_age, '\n Gender:' || passenger_gender as Details, booked FROM seats_{train_number} ORDER BY seat_number ASC''')

        result = seat_query.fetchall()

        if result:
            st.dataframe(data=result)


#booked ticket:

def book_tickets(train_number, passenger_name, passenger_age, passenger_gender, seat_type):
    global seat_number
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data = train_query.fetchone()

    if train_data:
        seat_number = allocate_next_available_seat(train_number, seat_type)

    if seat_number:
        c.execute(
            f"UPDATE seats_{train_number} SET booked=1, seat_type=?, passenger_name=?, passenger_age=?, passenger_gender=?"
            f"WHERE seat_number=?", (seat_type, passenger_name, passenger_age, passenger_gender, seat_number[0]))

        conn.commit()
    st.success(f"BOOKED SUCCESSFULLY !!!")


#cancel tickets:

def cancel_tickets(train_number, seat_num):
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data = train_query.fetchone()

    if train_data:
        c.execute(
            f"UPDATE seats_{train_number} SET booked=0, passenger_name='', passenger_age='',passenger_gender='' WHERE seat_num=?",
            (seat_num,))

        conn.commit()
        st.success(f"CANCELLED SUCCESSFULLY !!!")

#Delete train:

def  delete_tarin(train_number, departure_date):
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data = train_query.fetchone()

    if train_data:
        c.execute("DELETE FROM trains WHERE train_number=? AND departure_date=? ", (train_number,departure_date))
        conn.commit()
        st.success(f"DELETED SUCCESSFULLY !!!")


# apply all the functions:

def train_functions():

    st.title("Train Administrator")
    functions = st.sidebar.selectbox("select train functions",["Add train","view trains", "search train","cancel tickets","delete tarin","book tickets","view seats"])

    if functions == "add train":
        st.header("add new train")
        with st.form(key="new_train_details"):
            train_number = st.number_input("Enter train number")
            train_name = st.text_input("Enter train name")
            departure_date = st.text_input("Enter departure date")
            start_destination = st.text_input("Enter start destination")
            end_destination = st.text_input("Enter end destination")
            submitted = st.form_submit_button(label="Add train")
            if submitted and train_name !="" and train_number !="" and start_destination !="" and end_destination !="":
                add_train(train_number, train_name, departure_date, start_destination, end_destination)
                st.success(f"Added train {train_name} successfully")

    elif functions == "view trains":
        st.title("View trains")
        train_query=c.execute("SELECT * FROM trains WHERE train_number=?")
        trains= train_query.fetchone()

    elif functions == "book tickets":
        st.title("Book tickets")
        train_number=st.text_input("Enter train number")
        seat_type=st.selectbox("seat_type",["window","Aisle","Middle"], index=0)
        passenger_name=st.text_input("Enter passenger name")
        passenger_age=st.number_input("Enter passenger age",min_value=1,max_value=120)
        passenger_gender=st.selectbox("passenger gender",["male","female"],index=0)

        if st.button("book tickets"):
            if train_number and passenger_name and passenger_age and passenger_gender:
                book_tickets(train_number,passenger_age,passenger_gender,seat_type)

    elif functions == "cancel tickets":
        st.title("Cancel tickets")
        train_number=st.text_input("Enter train number")
        seat_num=st.number_input("Enter seat number",min_value=1)
        if st.button("cancel tickets"):
            if train_number and seat_num:
                cancel_tickets(train_number,seat_num)

    elif functions == "view seats":
        st.title("View seats")
        train_number=st.text_input("Enter train number")
        if st.button("view seats"):
            if train_number:
                view_seats(train_number)

    elif functions == "delete tarin":
        st.title("Delete tarin")
        train_number=st.text_input("Enter train number")
        departure_date=st.date_input("Enter departure date")
        if st.button("delete tarin"):
            if train_number:
                c.execute(f"DROP TABLE IF EXISTS seats_{train_number}")
                delete_tarin(train_number, departure_date)





