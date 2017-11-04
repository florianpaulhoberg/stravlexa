#!/usr/local/bin/python
""" 
Name: stravlexa.py: An Alexa python skill to provide you your latest activities and your current weight on Strava. 
Autor: Florian Paul Hoberg <florian {at} hoberg.ch>
Info: To run this Skill you will need an external webserver with valid SSL certificates, Amazon Developer and Strava account with API access.
"""

import urllib2, json
from flask import Flask
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, '/')

def get_stats_user(userid, token):
    url = "https://www.strava.com/api/v3/athletes/" + userid
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Bearer ' + token)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())
    return data['weight'], data['firstname']

def get_stats_activities(userid, token):
    url = "https://www.strava.com/api/v3/athletes/" + userid + "/stats"
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Bearer ' + token)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())
    return data['recent_run_totals'], data['recent_ride_totals'], data['recent_swim_totals']

def create_summary(stats_user_weight, stats_user_firstname, stats_run, stats_ride, stats_swim):
    user_weight = str(stats_user_weight)
    user_firstname = str(stats_user_firstname)
    user_stats_run_count = str(stats_run['count'])
    user_stats_ride_count = str(stats_ride['count'])
    user_stats_swim_count = str(stats_swim['count'])
    user_stats_run_distance = str(stats_run['distance'])
    user_stats_ride_distance = str(stats_ride['distance'])
    user_stats_swim_distance = str(stats_swim['distance'])
    user_stats_run_elapsed_time = int(stats_run['elapsed_time'])
    user_stats_ride_elapsed_time = int(stats_ride['elapsed_time'])
    user_stats_swim_elapsed_time = int(stats_swim['elapsed_time'])
    user_stats_overall_time = (user_stats_run_elapsed_time + user_stats_ride_elapsed_time + user_stats_swim_elapsed_time) / 60 / 60
    user_stats_overall_time_str = str(user_stats_overall_time)
    output_summary_user = "Sportzusammenfassung fuer " + user_firstname + ". Dein Gewicht betraegt aktuell " + user_weight + "Kilogramm"
    output_summary_time = "Du hast insgesamt " + user_stats_overall_time_str + " Stunden mit Sport verbracht"
    output_summary_run = "Du warst " +  user_stats_run_count + " mal laufen"
    output_summary_ride = "Du warst " +  user_stats_ride_count + " mal Fahrrad fahren"
    output_summary_swim = "Du warst " +  user_stats_swim_count + " mal schwimmen"
    return output_summary_user, output_summary_time, output_summary_run, output_summary_ride, output_summary_swim

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'Du benoetigst fuer diesen Skill einen Strava Account und API Token.'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    speech_text = 'Gehst du schon zum Sport? Viel Spass!'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)

@ask.intent('AMAZON.CacnelIntent')
def cancel():
    speech_text = 'Gehst du schon zum Sport? Viel Spass!'
    return question(speech_text).reprompt(speech_text).simple_card(speech_text)

@ask.intent('GetEventsIntent')
def main():
    # Define your Strava userid and your API token
    userid = "YOUR-USERID"
    token = "YOUR-API-TOKEN"

    stats_user_weight, stats_user_firstname = get_stats_user(userid, token)
    stats_run, stats_ride, stats_swim = get_stats_activities(userid, token)

    output_summary_user, output_summary_time, output_summary_run, output_summary_ride, output_summary_swim = create_summary(stats_user_weight, stats_user_firstname, stats_run, stats_ride, stats_swim)
    speech_text = "<speak>\n"
    speech_text += str(output_summary_user)
    speech_text += str(output_summary_time)
    speech_text += str(output_summary_run)
    speech_text += str(output_summary_ride)
    speech_text += str(output_summary_swim)
    speech_text += "</speak>"
    return statement(speech_text).simple_card(speech_text)

main()

if __name__ == '__main__':
    app.run(host="0.0.0.0")
