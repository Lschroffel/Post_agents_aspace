import json
import requests
import time
import csv
import sys
from datetime import datetime

secretsVersion = input('To edit production server, enter the name of the \
secrets file without extension: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        secrets = __import__('secrets')
        print('Editing Development')
else:
    print('Editing Development')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

targetFile = input('Enter file name: ')

auth = requests.post(baseURL + '/users/' + user + '/login?password='
                     + password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('postNewPersonalAgents' + date + '.csv', 'w'))
f.writerow(['sortName'] + ['uri'])

csvfile = csv.DictReader(open(targetFile))

def get_multiple_names():
    names = []
    for i in range(1,4): #range of 3
        if i == 1:
            extension = ''
        else:
            extension = str(i)
        name = {}
        name['primary_name'] = row['primaryName'+extension]
        name['name_order'] = 'inverted'
        name['jsonmodel_type'] = 'name_person'
        name['rules'] = 'rda'
        name['sort_name'] = row['sortName'+extension]
        try:
            name['authority_id'] = row['authorityID'+extension]
            name['source'] = row['source'+extension]
        except ValueError:
            pass
        try:
            name['rest_of_name'] = row['restOfName'+extension]
        except ValueError:
            name['name_order'] = 'direct'
        try:
            name['fuller_form'] = row['fullerForm'+extension]
        except ValueError:
            pass
        try:
            name['title'] = row['title'+extension]
        except ValueError:
            pass
        try:
            name['prefix'] = row['prefix'+extension]
        except ValueError:
            pass
        try:
            name['suffix'] = row['suffix'+extension]
        except ValueError:
            pass
        try:
            name['dates'] = row['date'+extension]
        except ValueError:
            pass
        if i > 1:
            name['is_display_name'] = False
        if name['primary_name']:
            names.append(name)
        else:
            print("skipping name because empty primaryname xxxx!!!!!!")
    return names
        
        


for row in csvfile:
    agentRecord = {}
    names = get_multiple_names()

    if row['date'] != '':
        dates = []
        date = {}
        date['label'] = 'existence'
        date['jsonmodel_type'] = 'date'
        if row['expression'] != '':
            date['expression'] = row['expression']
            date['date_type'] = 'single'
        elif row['begin'] != '' and row['end'] != '':
            date['begin'] = row['begin']
            date['end'] = row['end']
            date['date_type'] = 'range'
        elif row['begin'] != '':
            date['begin'] = row['begin']
            date['date_type'] = 'single'
        elif row['end'] != '':
            date['end'] = row['end']
            date['date_type'] = 'single'
        dates.append(date)
        agentRecord['dates_of_existence'] = dates
        print(dates)
    agentRecord['names'] = names
    agentRecord['publish'] = True
    agentRecord['jsonmodel_type'] = 'agent_person'
    agentRecord = json.dumps(agentRecord, indent=2)
    print(agentRecord)
    post = requests.post(baseURL + '/agents/people', headers=headers,
                         data=agentRecord).json()
    #print(json.dumps(post))
    print(json.dumps(post, indent=2))
    uri = post['uri']
    f.writerow([row['sortName']] + [uri])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
