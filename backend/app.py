from flask import Flask, render_template, request, url_for, redirect, session, flash
import bcrypt
import datetime
from db import users as records, unmerged_data, merged_data, db, user_logs
import requests
from wtforms import Form, StringField, SelectField

app = Flask(__name__)
app.secret_key = "testing"


class WeatherSearchForm(Form):
    choices = [("General", "General"), ("All", "All")]
    select = SelectField("Search for weather:", choices=choices)
    search = StringField("")


# assign URLs to have a particular route
@app.route("/register", methods=["post", "get"])
def index():
    message = ""
    # if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # if found in database showcase that it's found
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = "There already is a user by that name"
            return render_template("register.html", message=message)
        if email_found:
            message = "This email already exists in database"
            return render_template("register.html", message=message)
        if password1 != password2:
            message = "Passwords should match!"
            return render_template("register.html", message=message)
        else:
            # hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode("utf-8"), bcrypt.gensalt())
            # assing them in a dictionary in key value pairs
            user_input = {"name": user, "email": email, "password": hashed}
            # insert it in the record collection
            records.insert_one(user_input)

            # find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data["email"]
            # if registered redirect to logged in as the registered user
            return render_template("logged_in.html", email=new_email)
    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    message = "Please login to your account"
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found["email"]
            passwordcheck = email_found["password"]
            # encode the password and check if it matches
            if bcrypt.checkpw(password.encode("utf-8"), passwordcheck):
                session["email"] = email_val
                return redirect(url_for("logged_in"))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = "Wrong password"
                return render_template("login.html", message=message)
        else:
            message = "Email not found"
            return render_template("login.html", message=message)
    return render_template("login.html", message=message)


@app.route("/logged_in")
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template("logged_in.html", email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template("index.html")


@app.route("/", methods=["GET", "POST"])
def search_weather():
    search = WeatherSearchForm(request.form)
    if request.method == "POST":
        return search_results(search)
    if "email" in session:
        email = session["email"]
        return render_template("index.html", form=search, email=email)
    else:
        return render_template("index.html", form=search, email="")


@app.route("/results")
def search_results(search):
    results = []
    search_string = search.data["search"]
    if search.data["search"] == "":
        pass
    else:
        if search.data["select"] == "General":
            # results = merged_data.find_one({"city": search.data["search"]})
            results = merged_data.find_one(
                {
                    "city": search.data["search"],
                    "date": str(datetime.datetime.today().date()),
                }
            )
            if results == None:
                results = requests.get(
                    "http://localhost:8000/get_weather_on_city?city={}".format(
                        search.data["search"]
                    )
                ).json()["merged"]
        else:
            results = unmerged_data.find_one(
                {
                    "city": search.data["search"],
                    "date": str(datetime.datetime.today().date()),
                }
            )
            if results == None:
                results = requests.get(
                    "http://localhost:8000/get_weather_on_city?city={}".format(
                        search.data["search"]
                    )
                ).json()
    # results = False
    if not results:
        # flash("No results found!")
        return redirect("/")
    else:
        # display results
        return render_template("index.html", form=search, results=results)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
