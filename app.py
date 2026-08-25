# import the Flask class from the flask package

from flask import Flask, render_template, request, redirect 
from datetime import datetime
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
    db = sqlite3.connect("helpdesk.db")      # connect to the database file
    cursor = db.cursor()                     # get a cursor to run commands
    cursor.execute("SELECT * FROM tickets")    # get every row from the tickets table
    all_tickets = cursor.fetchall()            # pull the actual rows into a Python list
    db.close()                               # close the connection now that we're done
    print(all_tickets)                         # temporary: just print to terminal to verify
    return render_template("tickets.html", tickets=all_tickets)           # temporary placeholder response

@app.route("/new", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        # someone submitted the form — grab their data
        requester = request.form["requester"]
        description = request.form["description"]
        assigned_to = request.form["assigned_to"]
        priority = request.form["priority"]
        asset_id = request.form["asset_id"]
        resolution_notes = request.form["resolution_notes"]
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        already_resolved = request.form.get("already_resolved") == "yes"
        resolved_at = request.form.get("resolved_at") if already_resolved else None

        if already_resolved:
            status = "Fixed"
            resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            status = "Open"
            resolved_at = None

        conn = sqlite3.connect("helpdesk.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tickets (assigned_to, requester, description, priority, resolution_notes, status, created_at, asset_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (assigned_to, requester, description, priority, resolution_notes, status, created_at, asset_id))

        conn.commit()
        conn.close()

        # redirect back to the tickets list so they see it appear
        return redirect("/tickets")
    else:
        # show the blank form
        return render_template("new_ticket.html")



# this block only runs if you execute this file directly (not imported elsewhere)

if __name__ == "__main__":

    # start the built-in development server

    app.run()