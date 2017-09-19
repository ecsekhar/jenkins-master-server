#!/usr/bin/python
#
# check-mk local check for collecting Jenkins job statistics.
#
# NOTE: this script assumes that there is view named 'All' and it contains all jobs.

import requests, datetime, time, json, logging

STORAGE_FILE = '/var/check-mk/check-mk-jenkins-jobs-stats.json'
LOG_FILE = '/var/log/check-mk-jenkins/jenkins-builds.log'
JENKINS_SERVER_URL  = 'https://devops.org.com'
JENKINS_URL  = JENKINS_SERVER_URL + '/jenkins'
TIME_FORMAT  = '%b %d %Y %H:%M:%S GMT+0000'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

current_time = int(time.time())*1000

#Read data from previous check
try:
    with open(STORAGE_FILE) as storage_file:
        last_check = json.load(storage_file)
except:
   last_check = {'check_time': current_time - 7200*1000, 'total_job_count': 0, 'passed_job_count': 0, 'total_duration': 0, 'daily_job_count': 0, 'ongoing_jobs': []}

#Clear daily job count if day has changed
if datetime.datetime.fromtimestamp(current_time/1000).strftime('%d') != datetime.datetime.fromtimestamp(last_check['check_time']/1000).strftime('%d'):
     last_check['daily_job_count'] = 0

#Check status of ongoing jobs from last check
for i, job in enumerate(last_check['ongoing_jobs']):
    try:
        job_status =  requests.get( JENKINS_SERVER_URL + job + 'api/json?pretty=true&tree=duration,building,result,actions[causes[shortDescription]]').json()
        #Update counters and write log if job is finished
        if job_status['building'] == False:
            last_check['total_duration'] += int(job_status['duration']/1000)
            if job_status['result'] == 'SUCCESS':
                last_check['passed_job_count'] += 1
            last_check['ongoing_jobs'][i] = ''
            causes = [item for item in job_status['actions'] if 'causes' in item]
            cause = causes[0]['causes'][0]['shortDescription'] if causes else 'no cause'
            logging.info('END   ' + job + ': ' + job_status['result'] + ', ' + str(job_status['duration']) + ', ' + cause)
    except:
        logging.exception('Error in checking jobs status: ' + job)
        #Remove from pending tasks
        last_check['ongoing_jobs'][i] = ''

#Remove checked jobs, i.e. empty strings
last_check['ongoing_jobs'] = filter(None, last_check['ongoing_jobs'])


#Get jobs that have been started since the last check
new_jobs = requests.get(JENKINS_URL + '/view/All/timeline/data?min=' + str(last_check['check_time']) + '&max=' + str(current_time)).json()

last_check['total_job_count'] += len(new_jobs['events'])
last_check['daily_job_count'] += len(new_jobs['events'])

#Save new ongoing jobs since last check and write started jobs to the log
for job in new_jobs['events']:
    last_check['ongoing_jobs'].append(job['link'])
    logging.info('START ' + job['link'] + ': ' + job['start'])

#Ensure no duplicate values, this should not be needed but is extra precaution.
last_check['ongoing_jobs'] = list(set(last_check['ongoing_jobs']))


last_check['check_time'] = current_time

#Save data to file to be used at next check
with open(STORAGE_FILE, 'w') as storage_file:
    json.dump(last_check, storage_file, indent=4, sort_keys=True, ensure_ascii=False)

print "0 jenkins_jobs total=%dc|passed=%dc|failed=%dc|ongoing=%d|duration=%dc|daily=%d Jenkins jobs check" % (
    last_check['total_job_count'],
    last_check['passed_job_count'],
    last_check['total_job_count']-last_check['passed_job_count']-len(last_check['ongoing_jobs']),
    len(last_check['ongoing_jobs']),
    last_check['total_duration'],
    last_check['daily_job_count'])
