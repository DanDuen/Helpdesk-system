# import the Flask class from the flask package

from flask import Flask, render_template

# create an instance of the Flask application

# __name__ is a special Python variable that tells Flask

# where to look for things like templates later on

app = Flask(__name__)

# this "decorator" tells Flask: when someone visits the "/" URL (the homepage),

# run the function defined right below it

@app.route("/")

def home():
    return render_template("home.html")

    # whatever this function returns becomes the response sent to the browser

    return "Connection successful"

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