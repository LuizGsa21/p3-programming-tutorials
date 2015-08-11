#!/bin/sh
apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip

pip install bleach
pip install oauth2client
pip install unidecode
pip install requests
pip install Flask-OAuth
pip install httplib2
pip install Flask-WTF
pip install Flask-SQLAlchemy
pip install Flask-Login
#pip install Flask-Mail
#pip install marshmallow
pip install -U marshmallow --pre
#pip install Flask-Babel

sudo apt-get -y install python-dev python-setuptools && \
sudo apt-get -y install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk && \
sudo pip install Pillow


su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'
su vagrant -c 'createdb test'
sudo -u postgres psql -c "ALTER USER vagrant WITH PASSWORD 'vagrant';"