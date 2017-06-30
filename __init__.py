from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'amafhh'
mongo = PyMongo(app, config_prefix='MONGO')

@app.route('/')
def homepage():
    return render_template("dashboard.html")

@app.route('/batting/')
def batting():
    player_name, runs, balls_played, total_matches, total_innings, highest_score, hundreds, fifties, thirties, ducks, average = get_player_batting_stats()
    return render_template("batting.html", player_stats=zip(player_name, runs, balls_played, total_matches, total_innings, highest_score, hundreds, fifties, thirties, ducks, average))


@app.route('/player/<player_name>')
def player_stats(player_name):
    players, total_matches, overs, total_runs, maidens, total_wickets, best_figures, five_wicket, three_wicket, total_wides, total_no_balls, economoy, avg= get_player_bowling_stats(player_name)
    player_name, runs, balls_played, total_matches, total_innings, highest_score, hundreds, fifties, thirties, ducks, average = get_player_batting_stats(player_name)
    return render_template("player.html", bowl_stats=zip(players, total_matches, overs, total_runs, maidens, total_wickets, best_figures, five_wicket, three_wicket, total_wides, total_no_balls, economoy, avg), bat_stats=zip(player_name, runs, balls_played, total_matches, total_innings, highest_score, hundreds, fifties, thirties, ducks, average))


@app.route('/matchHistory')
def match_history():
    pass

@app.route('/stats/')
def stats():
    total_played = mongo.db.statistics.count()
    win_count = mongo.db.statistics.count({"Result":"Won"})
    loss_count = mongo.db.statistics.count({"Result":"Loss"})
    denominator = win_count + float(loss_count)
    win_percent = float(win_count)/denominator
    win_percentage = round(win_percent*100, 2)
    return render_template("stats.html", total_played=total_played, win_count=win_count, loss_count=loss_count, win_percentage=win_percentage)


@app.route('/bowling/')
def bowling():
    players, total_matches, overs, total_runs, maidens, total_wickets, best_figures, five_wicket, three_wicket, total_wides, total_no_balls, economoy, avg= get_player_bowling_stats()
    return render_template("bowling.html", player_stats=zip(players, total_matches, overs, total_runs, maidens, total_wickets, best_figures, five_wicket, three_wicket, total_wides, total_no_balls, economoy, avg))


def get_player_bowling_stats(playerName=None):
    players = []
    total_runs = []
    overs = []
    economoy = []
    maidens = []
    matches =[]
    avg = []
    total_wickets = []
    three_wicket = []
    five_wicket = []
    total_wides = []
    total_no_balls = []
    best_figures = []
    if playerName is not None:
        player_stats = mongo.db.players.find({"Player Name": playerName})
        for stats in player_stats:
            total_innings, total_matches = _get_number_of_innings(stats['Player Name'])
            bowling_avg = _calculate_bowling_average(stats['total_runs_conceded'], stats['total_wickets'])
            eco = _calculate_bowling_economy(stats['total_runs_conceded'], stats['Overs'])
            best = _calculate_best_figures(stats['runs_conceded'], stats['Wickets'])
            five = _get_five_wicket_haul(stats['Wickets'])
            three = _get_three_wicket_haul(stats['Wickets'])

            total_runs.append(stats['total_runs_conceded'])
            players.append(stats['Player Name'])
            total_wickets.append(stats['total_wickets'])
            total_wides.append(stats['total_wides'])
            total_no_balls.append(stats['total_no_balls'])
            maidens.append(stats['Maidens'])
            matches.append(total_matches)
            avg.append(bowling_avg)
            economoy.append(eco)
            overs.append(stats['Overs'])
            best_figures.append(best)
            five_wicket.append(five)
            three_wicket.append(three)
        return players, matches, overs, total_runs, maidens, total_wickets, best_figures, five_wicket, three_wicket, total_wides, total_no_balls, economoy, avg


    else:
        players_name = mongo.db.players.distinct("Player Name")
        for player in players_name:
            player_stats = mongo.db.players.find({"Player Name": player})
            for stats in player_stats:
                total_innings, total_matches = _get_number_of_innings(stats['Player Name'])
                bowling_avg = _calculate_bowling_average(stats['total_runs_conceded'], stats['total_wickets'])
                eco = _calculate_bowling_economy(stats['total_runs_conceded'], stats['Overs'])
                best = _calculate_best_figures(stats['runs_conceded'], stats['Wickets'])
                five = _get_five_wicket_haul(stats['Wickets'])
                three = _get_three_wicket_haul(stats['Wickets'])

                total_runs.append(stats['total_runs_conceded'])
                players.append(stats['Player Name'])
                total_wickets.append(stats['total_wickets'])
                total_wides.append(stats['total_wides'])
                total_no_balls.append(stats['total_no_balls'])
                maidens.append(stats['Maidens'])
                matches.append(total_matches)
                avg.append(bowling_avg)
                economoy.append(eco)
                overs.append(stats['Overs'])
                best_figures.append(best)
                five_wicket.append(five)
                three_wicket.append(three)
        return players, matches, overs, total_runs, maidens, total_wickets, best_figures, five_wicket, three_wicket, total_wides, total_no_balls, economoy, avg


def _calculate_best_figures(runs_conceded, wickets):
    temp = 0
    w = 0
    r = 99999
    for i in range(len(wickets)):
            if int(wickets[i]) >= temp:
                w = int(wickets[i])
                if int(runs_conceded[i]) < r:
                    r = int(runs_conceded[i])
                temp = int(wickets[i])


    best_figures = "%d / %d" %(w,r)
    return best_figures

def _get_five_wicket_haul(wickets):
    count = 0
    for wicket in wickets:
        if int(wicket) >= 5:
            count = count + 1
    return count

def _get_three_wicket_haul(wickets):
    count = 0
    for wicket in wickets:
        if int(wicket) >= 3 and int(wicket) < 5:
            count = count + 1
    return count

def _calculate_bowling_economy(total_runs_conceded, overs):
    if total_runs_conceded == "0" or overs == "0":
        return 0
    eco = int(total_runs_conceded)/float(overs)
    return round(eco,2)

def _calculate_bowling_average(total_runs_conceded, total_wickets):
    if total_wickets == "0" or total_runs_conceded == "0":
        return 0
    bowling_avg = int(total_runs_conceded)/float(total_wickets)
    return round(bowling_avg,2)




def get_player_batting_stats(playerName=None):
    players = []
    runs = []
    balls_played = []
    innings = []
    matches = []
    hs = []
    hundreds = []
    fifties = []
    thirties = []
    ducks = []
    average = []
    if playerName is not None:
        player_stats = mongo.db.players.find({"Player Name": playerName})
        for stats in player_stats:
            total_innings, total_matches = _get_number_of_innings(stats['Player Name'])
            highest_score = _get_highest_score(stats['Player Name'])
            hundred = _get_hundreds(stats['runs'])
            fifty = _get_fifties(stats['runs'])
            thirty = _get_thirties(stats['runs'])
            duck = _get_ducks(stats['runs'], stats['Dismissal'])
            avg = _calculate_batting_average(stats['total_runs'], total_innings, stats['Dismissal'])

            average.append(avg)
            ducks.append(duck)
            hundreds.append(hundred)
            fifties.append(fifty)
            thirties.append(thirty)
            players.append(stats['Player Name'])
            runs.append(stats['total_runs'])
            balls_played.append(stats['Balls Played'])
            innings.append(total_innings)
            matches.append(total_matches)
            hs.append(highest_score)
        return players, runs, balls_played, matches, innings, hs, hundreds, fifties, thirties, ducks, average

    else:
        players_name = mongo.db.players.distinct("Player Name")
        for player in players_name:
            player_stats = mongo.db.players.find({"Player Name":player})
            for stats in player_stats:
                total_innings, total_matches = _get_number_of_innings(stats['Player Name'])
                highest_score = _get_highest_score(stats['Player Name'])
                hundred = _get_hundreds(stats['runs'])
                fifty = _get_fifties(stats['runs'])
                thirty = _get_thirties(stats['runs'])
                duck = _get_ducks(stats['runs'], stats['Dismissal'])
                avg = _calculate_batting_average(stats['total_runs'], total_innings, stats['Dismissal'])

                average.append(avg)
                ducks.append(duck)
                hundreds.append(hundred)
                fifties.append(fifty)
                thirties.append(thirty)
                players.append(stats['Player Name'])
                runs.append(stats['total_runs'])
                balls_played.append(stats['Balls Played'])
                innings.append(total_innings)
                matches.append(total_matches)
                hs.append(highest_score)
        return players,runs, balls_played,matches,innings,hs, hundreds, fifties, thirties, ducks, average


def _calculate_batting_average(total_runs, total_innings, dismissals):
    not_outs = 0
    for dismissal in dismissals:
        if dismissal == "Not Out":
            not_outs = not_outs + 1
    denominator = float(total_innings) - not_outs
    if denominator == 0:
        average = int(total_runs)/float(total_innings)
    else:
        average = int(total_runs)/denominator
    return round(average,2)


def _get_hundreds(runs):
    hundreds = 0
    for run in runs:
        if int(run) >= 100:
            hundreds = hundreds + 1
    return hundreds


def _get_fifties(runs):
    fifties = 0
    for run in runs:
        if int(run) >= 50 and int(run) < 100:
            fifties = fifties + 1
    return fifties


def _get_thirties(runs):
    thirties = 0
    for run in runs:
        if int(run) >= 30 and int(run) < 50:
            thirties = thirties + 1
    return thirties


def _get_ducks(runs, dismissals):
    ducks = 0
    for run, dismissal in zip(runs, dismissals):
        if int(run) == 0 and dismissal != "DNB":
            ducks = ducks + 1
    return ducks


def _get_highest_score(playerName):
    all_runs = mongo.db.players.find({"Player Name":playerName},{"runs":1, "_id":0})
    for val in all_runs:
        runs_list = map(int, val['runs'])
    runs_list.sort()
    return runs_list[-1]

def _get_number_of_innings(playerName):
    count = 0
    innings = mongo.db.players.find({"Player Name":playerName},{"Dismissal":1, "_id":0})
    for inn in innings:
        total_matches = len(inn['Dismissal'])
        for dismissal in inn['Dismissal']:
            if dismissal != "DNB":
                count = count +1
    return count, total_matches


@app.route('/dashboard/')
def dashboard():
    # total_played = mongo.db.statistics.count()
    # win_count = mongo.db.statistics.count({"Result":"Won"})
    # loss_count = mongo.db.statistics.count({"Result":"Loss"})
    # win_percentage = ((win_count + loss_count)/win_count)*100
    return render_template("dashboard.html")

@app.route('/match/', methods=['GET', 'POST'])
def match():
    return render_template("newMatch.html")
    new_match()


@app.route('/createMatch/', methods=['GET','POST'])
def create_match():
    return render_template("newMatch.html")


@app.route('/newMatch/', methods=['GET', 'POST'])
def new_match():
    player = []
    runs = []
    balls_faced=[]
    wickets = []
    overs=[]
    maidens=[]
    wides=[]
    no_balls = []
    runs_conceded=[]
    dismissal = []
    if request.method == "POST":
        date = datetime.now()
        match_id = mongo.db.statistics.insert({'date': date})
        match_id = ObjectId(match_id)
        result = request.form
        match_format = result.get('Format')
        Opposition = result.get('Opposition')
        match_result = result.get('Result')
        amafhh_score = result.get('HomeTotal')
        tournament = result.get('Tournaments')
        opposition_score = result.get('AwayTotal')

        mongo.db.statistics.update({'_id':match_id},{"Opposition":Opposition,
                                                    "Format":match_format,
                                                    "Result":match_result,
                                                    "AmaffhScore":amafhh_score,
                                                     "Tournaments":tournament,
                                                    "OppositionScore":opposition_score})
    for key in result.keys():
        for value in result.getlist(key):
            if key=="playerName":
                player.append(value)
            if key == "Runs":
                runs.append(value)
            if key == "BallsFaced":
                balls_faced.append(value)
            if key == "Wickets":
                wickets.append(value)
            if key == "Overs":
                overs.append(value)
            if key == "Maidens":
                maidens.append(value)
            if key == "RunsConceded":
                runs_conceded.append(value)
            if key == "Wides":
                wides.append(value)
            if key == "NoBalls":
                no_balls.append(value)
            if key == "dismissal":
                dismissal.append(value)

    for playerName, runs, balls_faced, wickets, overs, maidens, runs_conceded, wides, no_balls, dismissal in zip(player, runs, balls_faced, wickets, overs, maidens, runs_conceded, wides, no_balls, dismissal):
        mongo.db.statistics.update({'_id':match_id},
                                        {'$push' : {"players": {'Player Name':playerName,
                                                                'runs': runs,
                                                                'Balls Played': balls_faced,
                                                                'Wickets': wickets,
                                                                'Overs': overs,
                                                                'Maidens': maidens,
                                                                'Wides':wides,
                                                                'NoBalls':no_balls,
                                                                'RunsConceded':runs_conceded,
                                                                'Dismissal': dismissal}}})

        total_runs,balls_faced,total_wickets,overs,maidens, total_runs_conceded, total_wides, total_no_balls = get_aggregated_stats(playerName, runs, balls_faced, wickets, overs, maidens, runs_conceded, wides, no_balls)
        if _check_player_exists(playerName):
            mongo.db.players.update({'Player Name':playerName}, {'$set': {'Player Name':playerName,
                                                                    'Balls Played': balls_faced,
                                                                    'Overs': overs,
                                                                    'Maidens': maidens,
                                                                    'total_runs_conceded': total_runs_conceded,
                                                                    'total_runs': total_runs,
                                                                    'total_wickets':total_wickets,
                                                                    'total_wides':total_wides,
                                                                    'total_no_balls':total_no_balls
                                                                 }})
        else:
            mongo.db.players.insert({'Player Name':playerName,
                                    'Balls Played': balls_faced,
                                    'total_wickets': total_wickets,
                                    'total_runs': total_runs,
                                     'Overs':overs,
                                     'Maidens': maidens,
                                     'total_runs_conceded': total_runs_conceded,
                                     'total_wides': total_wides,
                                     'total_no_balls': total_no_balls
                                })

        mongo.db.players.update({'Player Name':playerName},{'$push':{'runs_conceded': runs_conceded}})
        mongo.db.players.update({'Player Name':playerName},{'$push':{'Wickets': wickets}})
        mongo.db.players.update({'Player Name':playerName},{'$push':{'runs': runs}})
        mongo.db.players.update({'Player Name':playerName},{'$push':{'Dismissal':dismissal}})

    return render_template("main.html")

def _check_player_exists(playerName):
    player_exists = mongo.db.players.count({'Player Name': playerName})
    if player_exists == 0:
        return False
    return True

def get_aggregated_stats(playerName, runs, balls_faced, wickets, overs, maidens, runs_conceded, wides, no_balls):
    player_exists = mongo.db.players.count({'Player Name':playerName})
    if player_exists == 0:
        return runs, balls_faced, wickets, overs, maidens, runs_conceded, wides, no_balls
    else:
        player_stats = mongo.db.players.find({'Player Name':playerName})
    for doc in player_stats:
        try:
            total_runs = int(doc['total_runs']) + int(runs)
            total_balls_faced = int(doc['Balls Played']) + int(balls_faced)
            total_wickets = int(doc['total_wickets']) + int(wickets)
            total_overs = int(doc['Overs']) + int(overs)
            total_maidens = int(doc['Maidens']) + int(maidens)
            runs_conceded = int(doc['total_runs_conceded']) + int(runs_conceded)
            total_wides = int(doc['total_wides']) + int(wides)
            total_no_balls = int(doc['total_no_balls']) + int(no_balls)
        except ValueError:
            return runs,balls_faced,wickets,overs,maidens, runs_conceded, wides, no_balls
        return total_runs,total_balls_faced,total_wickets,total_overs,total_maidens, runs_conceded, total_wides, total_no_balls

if __name__ == "__main__":
    app.run()
