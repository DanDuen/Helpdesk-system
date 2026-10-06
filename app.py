# import the Flask class from the flask package
from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3

# create an instance of the Flask application
# __name__ is a special Python variable that tells Flask
# where to look for things like templates later on
app = Flask(__name__)

# create the database tables if they don't already exist yet
# this runs once, when the server starts, so a brand-new install
# (a new computer, a fresh clone of the repo) automatically gets
# a working, empty database without any manual setup steps
def init_db():
    conn = sqlite3.connect("helpdesk.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assigned_to TEXT,
            requester TEXT,
            description TEXT,
            priority TEXT,
            status TEXT,
            asset_id TEXT,
            created_at TEXT,
            resolved_at TEXT,
            resolution_notes TEXT,
            is_deleted INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER,
            note TEXT,
            created_at TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets (id)
        )
    """)

    conn.commit()
    conn.close()

# run the database setup every time this file is loaded, whether it was
# started with "python app.py" or "flask run" (safe to repeat, because
# CREATE TABLE IF NOT EXISTS skips tables that already exist)
init_db()

# this "decorator" tells Flask: when someone visits the "/" URL (the homepage),
# run the function defined right below it
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/tickets")
def list_tickets():
    db = sqlite3.connect("helpdesk.db")      # connect to the database file
    cursor = db.cursor()                     # get a cursor to run commands
    cursor.execute("SELECT * FROM tickets WHERE is_deleted = 0")    # get every row from the tickets table except those marked as deleted
    all_tickets = cursor.fetchall()            # pull the actual rows into a Python list
    db.close()                               # close the connection now that we're done
    #print(all_tickets)                         # temporary: just print to terminal to verify
    return render_template("tickets.html", tickets=all_tickets)

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
        created_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        already_resolved = request.form.get("already_resolved") == "yes"

        if already_resolved:
            status = "Fixed"
            resolved_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        else:
            status = "Open"
            resolved_at = None

        conn = sqlite3.connect("helpdesk.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tickets (assigned_to, requester, description, priority, resolution_notes, status, created_at, asset_id, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (assigned_to, requester, description, priority, resolution_notes, status, created_at, asset_id, resolved_at))

        conn.commit()
        conn.close()

        # redirect back to the tickets list so they see it appear
        return redirect("/tickets")
    else:
        # show the blank form
        return render_template("new_ticket.html")

@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    db = sqlite3.connect("helpdesk.db")
    cursor = db.cursor()
    #get info from the database for the ticket with the given ID
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = cursor.fetchone()

    #get all of the updates for this ticket from the updates table
    cursor.execute("SELECT * FROM updates WHERE ticket_id = ?", (ticket_id,))
    updates = cursor.fetchall()

    db.close()
    return render_template("ticket.html", ticket=ticket, updates=updates)

@app.route("/ticket/<int:ticket_id>/edit", methods=["GET", "POST"])
def edit_ticket(ticket_id):
    if request.method == "GET":
        db = sqlite3.connect("helpdesk.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        ticket = cursor.fetchone()
        db.close()
        return render_template("edit_ticket.html", ticket=ticket)
    else:
        # handle the form submission for editing the ticket
        requester = request.form["requester"]
        description = request.form["description"]
        assigned_to = request.form["assigned_to"]
        priority = request.form["priority"]
        asset_id = request.form["asset_id"]
        resolution_notes = request.form["resolution_notes"]
        already_resolved = request.form.get("already_resolved") == "yes"
        is_deleted = request.form.get("is_deleted") == "yes"

        if already_resolved:
            status = "Fixed"
            resolved_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        else:
            status = "Open"
            resolved_at = None

        conn = sqlite3.connect("helpdesk.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tickets
            SET assigned_to = ?, requester = ?, description = ?, priority = ?, resolution_notes = ?, status = ?, asset_id = ?, resolved_at = ?, is_deleted = ?
            WHERE id = ?
        """, (assigned_to, requester, description, priority, resolution_notes, status, asset_id, resolved_at, is_deleted, ticket_id))
        conn.commit()
        conn.close()

        return redirect(f"/ticket/{ticket_id}")

@app.route("/ticket/<int:ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    conn = sqlite3.connect("helpdesk.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET is_deleted = 1 WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    return redirect("/tickets")

@app.route("/ticket/<int:ticket_id>/update", methods=["POST"])
def add_update(ticket_id):
    # get the note text from the form — must match the textarea's name="..."
    note = request.form["note"]

    # generate a timestamp, same pattern as elsewhere
    created_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # connect to the database
    conn = sqlite3.connect("helpdesk.db")
    cursor = conn.cursor()

    # insert this note as a new row in the updates table
    cursor.execute("""
        INSERT INTO updates (ticket_id, note, created_at)
        VALUES (?, ?, ?)
    """, (ticket_id, note, created_at))

    # save the change and close the connection
    conn.commit()
    conn.close()

    # redirect back to the ticket's own page
    return redirect(f"/ticket/{ticket_id}")

#TODO: turn off debug mode when deploying to production
if __name__ == "__main__":
    app.run(debug=True)  # Start the Flask development server with debug mode enabled