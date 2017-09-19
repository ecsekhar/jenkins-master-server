# Description

This project sets up Jenkins master server.

# Installation

## Pre-requisites

* org wildcard certificate and key available (x.org.com.crt, x.org.com.key)

* Photon OS installed with following options:
  * Docker-compose
  * Git
  * Nagios (check-mk)
  * NTP server
  * Ports 80 and 443 opened

## Installation steps

1. Clone this repo:
   * ```git clone https://git.org.com/devops/jenkins-master-server.git```
2. Create .env file:
  * ```cp env-template .env```
  * ```vi .env``` (If defaults need changing)
3. Initialize Jenkins home directory (note options if you want to change Jenkins home location!):
  * ```./scripts/init-jenkins-home.sh```
4. Copy org wildcard certificate
  * mkdir nginx/conf/cert
  * cp /path/to/cert/x.org.com.cer nginx/conf/cert/
  * cp /path/to/cert/x.org.com.key nginx/conf/cert/
5. Build docker image:
  * ```docker-compose build```
6. Start the service:
  * ```docker-compose up -d```
7. Follow the wiki instructions for configuring the Jenkins master.

### *Option*: Jenkins home location
By default Jenkins home is in */jenkins-home*. If you want ot change this edit the following files:
  * ```scripts/create-repo-dirs.sh```
  * ```.env```

### *Option*: Jenkins url
By default the Jenkins url is *\<server-name\>/jenkins*. If you want to change this edit the prefix value of *JENKINS_OPTS* parameter in file:
  * ```.env```

### *Option*: ssh key comment
By default ssh key comment is *Jenkins rsa key*. If you want to change this to something more specific edit ```scripts/create-repo-dirs.sh``` file.

### *Option*: Custom styles
There are custom css files in */jenkins-home/userContent* directory. If you want to use one configure it in Jenkins user interface:
  * _Manage Jenkins -> Configure System -> Themes_:
  * _URL of theme CSS_: ```http://<jenkins-server-url>/userContent/jenkins-material-theme-green.css```

### *Option*: DevOps home page
If you don't want to show DevOps home page remove the location from nginx.conf.


## Nagios local check
NOTE: This local check also writes Jenkins build log.
  1. ```mkdir /var/check-mk```
  2. ```cp nagios/check-mk-jenkins-jobs-stats.py /usr/lib/check_mk_agent/local/```
  3. ```vi /usr/lib/check_mk_agent/local/``` and change the Jenkins url if needed.
  4. ```mkdir /var/log/check-mk-jenkins```
  5. ```chmod o+xr /var/log/check-mk-jenkins```
  6. Install logrotate and configure rotation.
  7. Activate new statistics from Nagios.

# Links

[wiki](http://wiki.org.com/confluence/display/DEVOPS/DevOps+Adm+-+Jenkins+Master+Setup)

# Notes
org is the organization
