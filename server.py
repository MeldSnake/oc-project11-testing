import json
from flask import Flask,render_template,request,redirect,flash,url_for,abort


CLUBS_DATA_FILE = 'clubs.json'
COMPETITIONS_DATA_FILE = 'competitions.json'
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"


def loadClubs():
    with open(CLUBS_DATA_FILE) as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open(COMPETITIONS_DATA_FILE) as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']].pop()
    except IndexError:
        flash("Invalid mail address")
        return redirect(url_for("index"))
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    max_places = max(
        0,
        min(
            12,
            int(foundClub["points"]),
            int(foundCompetition["numberOfPlaces"]),
        ),
    )
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition,max_places=max_places)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    if placesRequired < 0 or placesRequired > min(12, int(club["points"]), int(competition["numberOfPlaces"])):
        abort(400)
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display
@app.route('/pointsDisplay')
def pointsDisplay():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))