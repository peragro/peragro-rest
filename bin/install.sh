#!/bin/sh

sudo apt-get install -qq git
sudo apt-get install -qq python-virtualenv
sudo apt-get install -qq python-pip
sudo apt-get install python-software-properties

mkdir DAMN
cd DAMN
mkdir store


virtualenv env
source env/bin/activate

git clone https://github.com/sueastside/damn-at.git
git clone https://github.com/sueastside/damn-index.git
git clone https://github.com/sueastside/damn-rest.git
git clone https://github.com/sueastside/django-project.git

#../env/bin/python setup.py develop



yes | sudo add-apt-repository ppa:irie/blender
yes | sudo add-apt-repository ppa:nickstenning/elasticsearch
sudo apt-get update -qq

sudo apt-get install -qq blender
sudo apt-get install -qq elasticsearch

pip install --user Image
pip install --user Yapsy
pip install --user thrift
pip install --user metrology

pip install --user django-autoslug
pip install --user django-reversion
pip install --user south
pip install --user pytz
pip install --user django-notifications-hq
pip install --user django-follow
