import requests
import json
import sqlite3
from tkinter import *
from tkinter.ttk import *
from tkinter import scrolledtext
import matplotlib.pyplot as plt
import random


def request_car():
    url = "https://random-data-api.com/api/vehicle/random_vehicle"
    response = requests.request("GET", url)
    return json.loads(response.text)


def random_color():
    return '#{:06x}'.format(random.randint(0, 0xFFFFFF))


def db_get_connection(filename='car.db'):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        return conn
    except Exception as e:
        print(e)
    return conn


def db_execute(conn, query):
    try:
        c = conn.cursor()
        c.execute(query)
    except Exception as e:
        print(e)


def db_init():
    query = """ CREATE TABLE IF NOT EXISTS Cars (
                                            make_and_model text NOT NULL, 
                                            car_type text, 
                                            color text, 
                                            kilometer_age REAL
                                        ); """
    conn = db_get_connection()
    if conn is not None:
        db_execute(conn, query)
    else:
        print("Could not initialize database. In db_init()")
    return conn


def db_all_cars(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Cars")
    rows = cur.fetchall()
    return rows


def db_add_car(conn):
    car = request_car()
    if car["make_and_model"] is None:
        return
    sql_query = 'INSERT INTO Cars (make_and_model, car_type, color, kilometer_age) VALUES (?,?,?,?)'
    conn.execute(sql_query, (
        car["make_and_model"],
        car["car_type"],
        car["color"],
        car["kilometrage"]))
    conn.commit()


def db_clear(conn):
    sql = 'DELETE FROM Cars'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def get_avg(arr):
    if len(arr) < 1:
        return 0
    total = 0
    for item in arr:
        total += item
    return total/len(arr)


def create_app(conn):

    def set_random_color():
        col = random_color()
        my_string_var.set("Color: " + col)
        window.configure(bg=col)

    def clear_db():
        db_clear(conn)

    def add_car():
        db_add_car(conn)

    def popup_db():

        new_window = Toplevel(window)
        cars = db_all_cars(conn)

        new_window.title("Database")
        Label(new_window, text="Output").grid(row=0, column=0, padx=15, pady=15, ipadx=10, ipady=10)
        txt = scrolledtext.ScrolledText(new_window)
        txt.grid(row=1, column=0, padx=15, pady=15, ipadx=10, ipady=10)
        for car in cars:
            txt.insert(END, ("- " + car[0] + "\t" + car[1] + "\t" + car[2] + "\t" + str(car[3]) + "\n"))

    def popup_stats():

        new_window = Toplevel(window)
        cars = db_all_cars(conn)
        kmgs = []
        for car in cars:
            kmgs.append(car[3])
        new_window.title("Car Conditions")
        Label(new_window, text="Output").grid(row=0, column=0, padx=15, pady=15, ipadx=10, ipady=10)
        txt = scrolledtext.ScrolledText(new_window)
        txt.grid(row=1, column=0, padx=15, pady=15, ipadx=10, ipady=10)
        txt.insert(END, ("- " + "Average distance travelled: " + str(get_avg(kmgs)) + "\n"))
        txt.insert(END, ("- " + "  Min   distance travelled: " + str(min(kmgs)) + "\n"))
        txt.insert(END, ("- " + "  Max   distance travelled: " + str(max(kmgs)) + "\n"))

    def popup_plot():

        new_window = Toplevel(window)
        cars = db_all_cars(conn)
        x = range(len(cars))
        kmgs = []
        for car in cars:
            kmgs.append(car[3])
        new_window.title("Kilometrages of All Cars")
        Label(new_window, text="Output").grid(row=0, column=0, padx=15, pady=15, ipadx=10, ipady=10)
        plt.bar(x, kmgs)
        plt.savefig('plot.png')
        render = PhotoImage(file="plot.png")
        img = Label(new_window, image=render)
        img.image = render
        img.grid(row=1, column=0, pady=10, ipady=10)

    window = Tk()
    my_string_var = StringVar()

    title = Label(window, text="Welcome to Car Database", width=50)
    btn_popup_db = Button(window, text="Database Output", command=popup_db)
    btn_popup_stats = Button(window, text="Kilometrage Stats", command=popup_stats)
    btn_popup_plot = Button(window, text="Kilometrage Plot", command=popup_plot)
    btn_add_car = Button(window, text="Add a Car", command=add_car)
    btn_clear_db = Button(window, text="Clear", command=clear_db)
    btn_color = Button(window, text="Random Color", command=set_random_color)
    lbl_color = Label(window, textvariable=my_string_var)

    window.title("Cars")
    window.configure(bg='#666')
    title.configure(anchor="center")

    title.grid(row=0, column=0, padx=40, pady=30, ipady=10, sticky="ew")
    btn_popup_db.grid(row=1, column=0, padx=150, pady=10, sticky="ew")
    btn_popup_stats.grid(row=2, column=0, padx=150, pady=10, sticky="ew")
    btn_popup_plot.grid(row=3, column=0, padx=150, pady=10, sticky="ew")
    btn_add_car.grid(row=4, column=0, padx=150, pady=10, sticky="ew")
    btn_clear_db.grid(row=5, column=0, padx=150, pady=10, sticky="ew")
    btn_color.grid(row=6, column=0, padx=150, pady=10, sticky="ew")
    lbl_color.grid(row=7, column=0, padx=80, pady=30, sticky="ew")

    title.focus()
    window.resizable(0, 0)
    window.mainloop()


def run():
    conn = db_init()
    create_app(conn)


if __name__ == "__main__":
    run()
