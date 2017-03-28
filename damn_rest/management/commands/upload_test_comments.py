import os
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.test.client import Client

import json

import random

s_nouns = ["A dude", "My mom", "The king", "Some guy", "A cat with rabies", "A sloth", "Your homie", "This cool guy my gardener met yesterday", "Superman"]
p_nouns = ["These dudes", "Both of my moms", "All the kings of the world", "Some guys", "All of a cattery's cats", "The multitude of sloths living under your bed", "Your homies", "Like, these, like, all these people", "Supermen"]
s_verbs = ["eats", "kicks", "gives", "treats", "meets with", "creates", "hacks", "configures", "spies on", "retards", "meows on", "flees from", "tries to automate", "explodes"]
p_verbs = ["eat", "kick", "give", "treat", "meet with", "create", "hack", "configure", "spy on", "retard", "meow on", "flee from", "try to automate", "explode"]
infinitives = ["to make a pie.", "for no apparent reason.", "because the sky is green.", "for a disease.", "to be able to make toast explode.", "to know more about archeology."]

def sing_sen_maker():
    data = random.choice(s_nouns), random.choice(s_verbs), random.choice(s_nouns).lower() or random.choice(p_nouns).lower(), random.choice(infinitives)
    return ' '.join(data)


class Command(BaseCommand):
    help = 'Upload test data set'

    def __init__(self):
        super(Command, self).__init__()
        self.c = Client()

    def login(self, username, password):
        # curl -X POST -d "username=admin&password=admin" http://damn.csproject.org:8081/api-token-auth/
        response = self.c.post('/api-token-auth/', {'username': 'admin', 'password': 'admin'})
        data = json.loads(response.content)
        self.token = data['token']

    def post(self, url, data):
        headers = {'HTTP_AUTHORIZATION': 'Token '+self.token}
        response = self.c.post(url, data, **headers)
        try:
            data = json.loads(response.content)
        except Exception as e:
            print(e)
            data = None
        return data, response

    def get(self, url):
        headers = {'HTTP_AUTHORIZATION': 'Token '+self.token}
        print('GET', url)
        response = self.c.get(url, follow=True, **headers)
        try:
            data = json.loads(response.content)
        except Exception as e:
            print('--------------------')
            print(response.status_code)
            print(e)
            print(response.content)
            print('--------------------')
            data = None
        return data, response

    def handle(self, *args, **options):
        print('uploading...')
        self.login('admin', 'admin')

        from django_project.models import Comment
        from damn_rest.models import Project
        from django.contrib.auth.models import User

        for c in Comment.objects.all():
            if hasattr(c.content_object, 'project') and c.content_object.project.name == 'Tempest In The Aether':
                c.delete()

        project_id = Project.objects.get(name='Tempest In The Aether').pk

        tasks_data, response = self.get('/projects/{project_id}/tasks/?page_size=99999'.format(project_id=project_id))

        for task in tasks_data['results']:
            task_id = task['id']
            #print task
            for i in range(5):
                data = {'comment': sing_sen_maker(),}
                data, response = self.post('/tasks/{task_id}/comments/'.format(task_id=task_id), data)
                print(data)
                comment_id = data['id']
                print(comment_id)


        for task in tasks_data['results']:
            task_id = task['id']
            data, response = self.get('/tasks/{task_id}/comments/'.format(task_id=task_id))
            assert data['count'] > 4
