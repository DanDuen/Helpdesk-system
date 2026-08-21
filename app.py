# import the Flask class from the flask package

from flask import Flask, render_template
import sqlite3
# create an instance of the Flask application

# __name__ is a special Python variable that tells Flask

# where to look for things like templates later on

app = Flask(__name__)

# this "decorator" tells Flask: when someone visits the "/" URL (the homepage),

# run the function defined right below it

@app.route("/")

def home():
    return render_template("home.html")

@app.route("/tickets")
def list_tickets():
    conn = sqlite3.connect("helpdesk.db")      # connect to the database file
    cursor = conn.cursor()                     # get a cursor to run commands
    cursor.execute("SELECT * FROM tickets")  # get every row from the tickets table
    all_tickets = cursor.fetchall()              # pull the actual rows into a Python list
    conn.close()                             # close the connection now that we're done
    print(all_tickets)                       # temporary: just print to terminal to verify
    return render_template("tickets.html", tickets=all_tickets)           # temporary placeholder response


@app.route("/about")
def about():
    return "This is the IT helpdesk system."

@app.route("/hello")

def hello():

    return "Hello, World!"

# this block only runs if you execute this file directly (not imported elsewhere)

if __name__ == "__main__":

    # start the built-in development server

    app.run()