#!/bin/sh
apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
pip install bleach
pip install oauth2client
pip install requests
pip install Flask-OAuth
pip install httplib2
pip install Flask-WTF
pip install Flask-SQLAlchemy
pip install beautifulsoup4
pip install Flask-Login
pip install Flask-OpenID
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'