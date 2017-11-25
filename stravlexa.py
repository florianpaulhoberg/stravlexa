#!/usr/bin/env python
""" 
Name: stravlexa.py: An Alexa python skill to provide you your latest activities and your current weight on Strava. 
Autor: Florian Paul Hoberg <florian {at} hoberg.ch>
Web: https://blog.hoberg.ch / https://github.com/florianpaulhoberg/stravlexa
Info: To run this Skill you will need an external webserver with valid SSL certificates, Amazon Developer and Strava account with API access.
"""

import urllib2, json
from flask import Flask
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, '/')

def get_stats_user(userid, token):
    """ Get athletes own information """
    url = "https://www.strava.com/api/v3/athletes/" + userid
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Bearer ' + token)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())
    return data['weight'], data['firstname'], data['username'], data['country'], data['city'], data['friend_count'], data['sex']

def get_stats_activities(userid, token):
    """ Get athletes last 30 activities """
    url = "https://www.strava.com/api/v3/activities"
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Bearer ' + token)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())
    return data

def split_activities(data, type_dict={}):
    """ Check for all activity types and split them """
    # Create an unique list in a dict of all
    # activity types within the last 30 activities
    for activity in data:
        activity_type = activity['type']
        if not activity_type in type_dict.keys():
            type_dict[activity_type] = [] 
    return type_dict

def generate_activities(data, type_dict):
    """ Split metrics for all activity types """
    # Copy created dict as template for every 
    # type of statistic to access the values
    # more easy at a later time
    time_dict = type_dict.copy()
    avg_heartrate_dict = type_dict.copy()
    avg_speed_dict = type_dict.copy()
    distance_dict = type_dict.copy()
    distance_dict = type_dict.copy()
    all_activitiy_types = []
    global_stats_time_dict = {}
    global_stats_heartrate_dict = {}
    global_stats_speed_dict = {}
    global_stats_distance_dict = {}
    global_count_dict = {}
 
    # split every activity type to it's corresponding
    # statistic dict 
    for activity in data:
        activity_type = activity['type']
        time_dict[activity_type] = time_dict[activity_type] + [ activity['elapsed_time'] ]
        avg_heartrate_dict[activity_type] = avg_heartrate_dict[activity_type] + [ activity['average_heartrate'] ]
        avg_speed_dict[activity_type] = avg_speed_dict[activity_type] + [ activity['average_speed'] ]
        distance_dict[activity_type] = distance_dict[activity_type] + [ activity['distance'] ]

        # Create an unique list of activity types
        if not activity_type in all_activitiy_types:
            all_activitiy_types.append(activity_type)

    for single_activity in all_activitiy_types:
        global_stats_time_dict[single_activity] = 0
        global_stats_heartrate_dict[single_activity] = 0
        # Speed value will be in meter per second
        # define this as float to convert it later
        # to kilometer per hour (European default)
        global_stats_speed_dict[single_activity] = 0.0
        global_stats_distance_dict[single_activity] = 0
        for value in time_dict[single_activity]:
            global_stats_time_dict[single_activity] = global_stats_time_dict[single_activity] + value
        for value in avg_heartrate_dict[single_activity]: 
            global_stats_heartrate_dict[single_activity] = global_stats_heartrate_dict[single_activity] + value
        for value in avg_speed_dict[single_activity]: 
            global_stats_speed_dict[single_activity] = global_stats_speed_dict[single_activity] + value
        for value in distance_dict[single_activity]: 
            global_stats_distance_dict[single_activity] = global_stats_distance_dict[single_activity] + value 

    # Get average values for every activity and option 
    for single_activity in all_activitiy_types:
        global_count_dict[single_activity] = len(time_dict[single_activity]) 
        global_stats_time_dict[single_activity] = global_stats_time_dict[single_activity] / len(time_dict[single_activity]) 
        global_stats_heartrate_dict[single_activity] = global_stats_heartrate_dict[single_activity] / len(avg_heartrate_dict[single_activity]) 
        global_stats_speed_dict[single_activity] = global_stats_speed_dict[single_activity] / len(avg_speed_dict[single_activity])
        global_stats_distance_dict[single_activity] = global_stats_distance_dict[single_activity] / len(distance_dict[single_activity])
        # convert meter per second to kilometer per hour
        global_stats_speed_dict[single_activity] = (float(global_stats_speed_dict[single_activity]) / 1000 * 3600)
    return global_stats_time_dict, global_stats_heartrate_dict, global_stats_speed_dict, global_stats_distance_dict, all_activitiy_types, global_count_dict

def overall_stats(data):
    """ Generate consolidated statistics over all activities """
    overall_activity_time = 0
    overall_activities = 0
    for activity in data:
        overall_activity_time = overall_activity_time + activity["elapsed_time"]
        overall_activities = len(activity.values())
    overall_activity_time = int(overall_activity_time) / 60 / 60
    return overall_activities, overall_activity_time

def translate_german(t_german = {}):
    """ Table of German translation of activities on Strava """
    t_german["Ride"] = "Fahrrad fahren"
    t_german["Run"] = "Laufen"
    t_german["Swim"] = "Schwimmen"
    t_german["WeightTraining"] = "Krafttraining"
    t_german["Walk"] = "Spazieren"
    t_german["Snowboard"] = "Snowboarden"
    t_german["EBikeRide"] = "Faules Radfahren" # just kidding
    t_german["Windsurf"] = "Surfen"
    t_german["IceSkating"] = "Eislaufen"
    t_german["InlineSkate"] = "Inline skaten"
    t_german["Canoeing"] = "Kanu fahren"
    t_german["Yoga"] = "Yoga"
    t_german["VirtualRide"] = "virtuelle Aktivitaet"
    return t_german

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
def main(count_activities={}):
    # Define your Strava userid and your API token
    userid = "<YOUR-USERID>"
    token = "<YOUR-API-TOKEN>"

    user_weight, user_firstname, user_username, user_country, user_city, user_friend_count, user_sex = get_stats_user(userid, token)
    data = get_stats_activities(userid, token)
    type_dict = split_activities(data)
    global_stats_time_dict, global_stats_heartrate_dict, global_stats_speed_dict, global_stats_distance_dict, all_activitiy_types, global_count_dict = generate_activities(data, type_dict)
    overall_activities, overall_activity_time = overall_stats(data)

    # Create German translateion
    global_stats_time_dict_ger = global_stats_time_dict.copy()
    global_stats_time_dict_ger = translate_german(global_stats_time_dict_ger)

    # Create speech event
    user_info = user_firstname + " du wiegst aktuell " + str(user_weight) + " Kilogramm "
    user_stats = "und hast in den letzten 30 Tagen " + str(overall_activities) + " Aktivitaeten in " + str(overall_activity_time) + " Stunden absolviert"

    # Create a list for every single activity for speech output
    activity_speech = []
    for single_activity in all_activitiy_types:
        activity_speech.append(global_stats_time_dict_ger[single_activity] + ": " + str(global_count_dict[single_activity]) + " mal. Im Schnitt: " + str(int(global_stats_distance_dict[single_activity])/1000) + " Kilometer zurueckgelegt " + str(int(global_stats_time_dict[single_activity]/60)) + " Minuten verbracht! Herzfrequenz: " + str(int(global_stats_heartrate_dict[single_activity])) + " Geschwindigkeit: " + str(int(global_stats_speed_dict[single_activity])) + " kmh")

    # Alexa speech output
    speech_text = "<speak>\n"
    speech_text += str(user_info)
    speech_text += str(user_stats)
    speech_text += str(activity_speech)
    speech_text += "</speak>"
    return statement(speech_text).simple_card(speech_text)

main()

if __name__ == '__main__':
    app.run(host="0.0.0.0")
