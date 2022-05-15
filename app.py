import requests
from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email  # EqualTo
# from yelp import find_coffee

class LoginForm(FlaskForm):
    email = StringField(label="Enter email",
                        validators=[DataRequired(), Email()])
    password = PasswordField(label="Enter password",
                             validators=[DataRequired(), Length(min=6, max=16)])
    submit = SubmitField(label="Login")

passwords = {
    'jpmont@uw.edu': 'qwerty',
}

class SearchForm(FlaskForm):
    date = DateField(label="Enter birthday",
                        validators=[DataRequired()])
    count = IntegerField(label="Number of results",
                             validators=[DataRequired(), NumberRange(min=1, max=20)])
    submit = SubmitField(label="Search")

canned_results = [
    {'name': 'George Washington', 'yearborn': 1743},
    {'name': 'Kermit the Frog', 'yearborn': 1968},
]

app = Flask(__name__, template_folder="templates")
app.secret_key = "sekrit"

def findBirths(monthDay, year, size=10):
    """
    monthDay is in form "mm/dd"
    year is in form "yyyy"
    returns a list of names, birth years and thumbnails
    sortedbyClosestYear[i]['text'] has name of ith match
    sortedbyClosestYear[i]['year'] has year of ith match's birthdate
    sortedbyClosestYear[i]['thumbnail'] has url of ith match's thumbnail picture or localhost if there is none
    """
    size = int(size)
    year = int(year)
    path = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday"
    response = requests.get(path + "/births/" + monthDay)
    data = response.json()
    sortedbyClosestYear = sorted(data["births"], key=lambda i: abs(int(i['year']) - year))
    if len(sortedbyClosestYear) > size:
        sortedbyClosestYear = sortedbyClosestYear[0:size]
    for item in sortedbyClosestYear:
        item['thumbnail'] = "localhost"
        if "thumbnail" in item['pages'][0]:
            item['thumbnail'] = item['pages'][0]["thumbnail"]["source"]
    return sortedbyClosestYear

@app.route("/home", methods=['GET', 'POST'])
def home():
    print("In home")
    results = []
    form = SearchForm()
    if request.method == "POST":
        print("Method POST")
        if form.validate_on_submit():
            # print("Validation ok")
            date = request.form["date"]
            count = request.form["count"]
            print(f"date='{date}' count='{count}'")
            dparts = date.split('-')
            year = dparts[0]
            month = dparts[1]
            day = dparts[2]
            dat = findBirths(f"{month}/{day}", year, size=count)
            print(dat)
            # TODO fetch actual results
            # results = canned_results
            results = []
            for d in dat:
                results.append({
                    'name': d['text'],
                    'year': d['year'],
                    # 'link': 'http://foo'
                    'img': d['thumbnail'],
                })
            print(results)
        else:
            print("Validation failed")
            pass
    else:
        print(f"Method {request.method}")
    return render_template("home.html", form=form, results=results)

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    # print("In login...")
    form = LoginForm()
    if request.method == "POST":
        # print("Method POST")
        if form.validate_on_submit():
            # print("Validation ok")
            user = request.form["email"]
            pw = request.form["password"]
            # print(f"user='{user}' pw='{pw}'")
            if user is not None and user in passwords and passwords[user] == pw:
                # print("Auth ok")
                return redirect('/home')
            print("Auth failed")
        else:
            print("Validation failed")
            pass
    else:
        # print(f"Method {request.method}")
        pass
    return render_template("login.html", form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

# END
