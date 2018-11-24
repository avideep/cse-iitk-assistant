#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import unicodedata

from flask import Flask
from flask import request
from flask import make_response
import requests
import string
import difflib

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['GET','POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    r = make_response(json.dumps(processRequest(req), indent=4))
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    action = req.get("queryResult").get("action")
    data = req 
    if action == "getPublicationYearURL":
        res = makeWebhookResultForGetPublicationYear(data)        
    elif action == "getPeopleNames":
        res = makeWebhookResultForGetPeopleNames(data)
    elif action == "getFacultyNames":
        res = makeWebhookResultForGetFacultyNames(data)
    elif action == "getCourseTimeWebPage":
        res = makeWebhookResultForGetCourseTimeWebPage(data)
    elif action == "getCourseName":
        res = makeWebhookResultForGetCourseName(data)
    elif action == "getScientist":
        res = makeWebhookResultForGetScientist(data)
    elif action == "getFacultyDetails":
        res = makeWebhookResultForGetFacultyDetails(data)
    elif action == "getCourseCode":
        res = makeWebhookResultForGetCourseCode(data)
    elif action == "getCommitteeName":
        res = makeWebhookResultForGetCommitteeName(data)
    else:
        return {'fulfillmentText' : 'I am sorry, I am a slow learner. Can you please repeat what you said?'}
    return res

def makeWebhookResultForGetCommitteeName(data):
    name = data.get("queryResult").get("parameters").get("committee")
    speech = "Sorry, Can you repeat that?"
    print(name)
    if name == "Head of the Department":
        speech = "The Head of the Department is Prof. Sandeep K. Shukla. Know more about him at https://www.cse.iitk.ac.in/users/sandeeps"
    elif name == "DPGC Convenor":
        speech = "The DPGC Convenor is Prof. Sumit Ganguly. Know more about him at https://www.cse.iitk.ac.in/users/sganguly/"
    elif name == "DUGC Convenor":
        speech = "The DUGC Convenor is Prof. Anil Seth. Know more about him at https://www.cse.iitk.ac.in/users/seth"
    
    return {'fulfillmentText' : speech  }

def makeWebhookResultForGetFacultyDetails(data):
    name = data.get("queryResult").get("parameters").get("faculty_names")
    name  = "".join((char for char in name if char not in string.punctuation))
    with open("faculty.json", "r") as read_file:
        faculty = json.load(read_file)
    all_prof_names = [str(i.get('name')) for i in faculty.get('prof_names')]
    possible_name_asked = difflib.get_close_matches(name,all_prof_names)
    if len(possible_name_asked) != 0:
        for i in faculty.get('prof_names'):
            if i.get('name') == possible_name_asked[0]:
                designation = str(i.get('designation'))
                url = str(i.get('designation_url'))
        speech = possible_name_asked[0] + ' is a(n) ' + designation + ' here. Know more about him/her at ' + url
    else:
        speech = name +' does not seem to be a faculty here. I can answer only name of the faculties here.' 
    return {'fulfillmentText' : speech  }

def makeWebhookResultForGetScientist(data):
    area = data.get("queryResult").get("parameters").get("research_area")
    area  = "".join((char for char in area if char not in string.punctuation))
    with open("research_area.json", "r") as read_file:
        research_areas = json.load(read_file)
    names = []
    all_research_areas = [str(i.get('name')) for i in research_areas.get('area')]
    possible_areas_asked = difflib.get_close_matches(area, all_research_areas)
    print(possible_areas_asked)
    for v in research_areas.get('area'):
        if v.get('name') in possible_areas_asked:
            faculty = v.get('faculty')
            if faculty is not None:
                faculty = str(faculty)
                names.append(faculty)
    if len(names) != 0:
        speech = ",".join(names) + ' work(s) in areas related to ' + area + '.'
    else:
        speech = 'Sorry, it seems nobody works in ' + area + '.'
    return {'fulfillmentText' : speech  }

def makeWebhookResultForGetCourseName(data):
    course_code = data.get("queryResult").get("parameters").get("course_code")
    course_code = course_code.replace(" ","").upper()
    with open("courses.json", "r") as read_file:
        courses = json.load(read_file)
    name = 'not found.'
    for i in courses.get('course'):
        if str(i.get('code')) == course_code:
            name = str(i.get('name'))
            break
    speech = 'The name of the course ' + course_code + ' is ' + name + '.'
    return {'fulfillmentText' : speech  }

def makeWebhookResultForGetCourseCode(data):
    course_name = data.get("queryResult").get("parameters").get("course_name")
    #course_code = course_code.replace(" ","").upper()
    with open("courses.json", "r") as read_file:
        courses = json.load(read_file)
    code = 'not found.'
    all_course_names = [str(i.get('name')) for i in courses.get('course')]
    possible_names_asked = difflib.get_close_matches(course_name, all_course_names)
    if len(possible_names_asked) != 0:
        for i in courses.get('course'):
            if i.get('name') == possible_names_asked[0]:
                code = str(i.get('code'))
                break
    speech = 'The code for the course ' + possible_names_asked[0] + ' is ' + code + '.'
    return {'fulfillmentText' : speech  } 

def makeWebhookResultForGetCourseTimeWebPage(data):
    course_time = data.get("queryResult").get("parameters").get("course_time")
    if course_time == 'next semester':
        website = 'https://cse.iitk.ac.in/pages/NextCourseTimetable.html'
    elif course_time == 'current semester':
        website = 'https://cse.iitk.ac.in/pages/CourseTimetable.html'
    elif course_time == 'previous semester':
        website = 'https://cse.iitk.ac.in/pages/PreviousCourseTimetable.html'
    speech = 'You can visit ' + website + ' to know about the ' + course_time + ' courses.'
    return {'fulfillmentText' : speech}

def makeWebhookResultForGetPublicationYear(data):
    year = data.get("queryResult").get("parameters").get("year")
    website = 'https://cse.iitk.ac.in/pages/ResearchPublication_'+str(year)+'.html'
    request = requests.get(website)
    if request.status_code == 200:
        speech = 'Head over to '+website+' to know about the publications of ' + str(year) + '.'
    else:
        speech = 'Sorry, there\'s no information available in the website about the publications from ' + year + '.'
    return {'fulfillmentText' : speech}

def makeWebhookResultForGetFacultyNames(data):
    designation = data.get("queryResult").get("parameters").get("designation_faculty")
    if designation in ['Professor','Associate Professor','Assistant Professor']:
        with open("faculty.json", "r") as read_file:
            faculty = json.load(read_file)
        name = []
        for i in faculty.get('prof_names'):
            if i.get('designation') == designation:
                name.append(i.get('name').encode('utf-8'))
        speech = ", ".join(name) + ' are the ' + designation + ' here.'
    elif designation == 'post-docs':
        with open("post_docs.json", "r") as read_file:
            post_docs = json.load(read_file)
        names = []
        for i in post_docs.get('post_docs'):
            names.append(i.get('name').encode('utf-8'))
        speech = ", ".join(names) + ' are the post-doctoral fellows here.'
    return {'fulfillmentText' : speech}

def makeWebhookResultForGetPeopleNames(data):
    designation = data.get("queryResult").get("parameters").get("designation")
    if designation == 'PhD':
        year = data.get("queryResult").get("parameters").get("number")
        with open("phd.json", "r") as read_file:
            phd = json.load(read_file)
        names = []
        year_ind = 2018 - int(year)
        website =  website = 'https://cse.iitk.ac.in/pages/'+designation+str(int(year))+'_Person.html'
        request = requests.get(website)
        if request.status_code == 200 and int(year) >= 2012:
            for i in phd.get('phd')[year_ind].get('name'):
                names.append(i.get('name').encode('utf-8'))
            speech = ", ".join(names) + ' are the students who joined in ' + str(int(year)) + ' and are pursuing ' + designation + ' here.' + '\n You can know more about them at ' + website
        else:
            speech = 'Sorry, there\'s no information available in the website about ' + designation +' students who joined in ' + year + '.'
    elif designation in ['MTech','BTech','MS','MTI']:
        year = str(int(data.get("queryResult").get("parameters").get("number")))
        website = 'https://cse.iitk.ac.in/pages/'+designation+year+'_Person.html'
        print(website)
        request = requests.get(website)
        if request.status_code == 200 and int(year) >= 2012: 
            speech = 'You can check the list of students who are studying '+designation+' here and joined in ' + year + ' at ' + website + '.'
            
        else:
            speech = 'Sorry, there\'s no information available in the website about ' + designation +' students who joined in ' + year + '.'
    return {'fulfillmentText' : speech}

if __name__ == '__main__':
    app.run()