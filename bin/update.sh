#!/bin/bash
cd damn-at/
git pull
cd ..

cd damn-index/
git pull
cd ..

cd damn-test-files/
git pull
cd ..

cd django-project/
git pull
cd ..

cd damn-rest/
git pull
rm db.sqlite3

source ../env/bin/activate
python manage.py syncdb
python manage.py migrate
