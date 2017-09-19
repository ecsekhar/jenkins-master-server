#!/bin/sh

JENKINS_HOME='/jenkins-home'

#Create Jenkins home directory
mkdir $JENKINS_HOME

#Create ssh keys:
mkdir $JENKINS_HOME/.ssh
ssh-keygen -t rsa -N '' -C 'Jenkins rsa key' -f $JENKINS_HOME/.ssh/id_rsa

#Copy styles to userContent:
mkdir $JENKINS_HOME/userContent
cp css/* $JENKINS_HOME/userContent/

#Change owner so Jenkins user in container can access the directory
chown -R 1000:1000 $JENKINS_HOME

