import os
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.test.client import Client

import json


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
            print e
            data = None
        return data, response

    def get(self, url):
        headers = {'HTTP_AUTHORIZATION': 'Token '+self.token}
        print 'GET', url
        response = self.c.get(url, follow=True, **headers)
        try:
            data = json.loads(response.content)
        except Exception as e:
            print '--------------------'
            print response.status_code
            print e
            print response.content
            print '--------------------'
            data = None
        return data, response

    def handle(self, *args, **options):
        print 'uploading...'
        self.login('admin', 'admin')

        from damn_rest.models import Project
        from django.contrib.auth.models import User

        Project.objects.filter(author__username='admin', name='Tempest In The Aether').delete()


        #curl -X POST -H "Authorization: Token 73aa7a873b055fb6dead287a526e85b79c0c0126" -d "name=Blah&description=dfddd&form=ddd" http://localhost/projects/
        data = {'name': 'Tempest In The Aether', 'description': "Steam punk without the '80s"}
        data, response = self.post('/projects/', data)
        project_id = data['id']
        print project_id

        data = {'name': 'Modeling', 'description': "Everything related to modeling", 'order': 0}
        data, response = self.post('/projects/{project_id}/tasktypes/'.format(project_id=project_id), data)
        tasktype_url = data['url']
        print tasktype_url

        data = {'name': 'High', 'description': "High priority", 'order': 0}
        data, response = self.post('/projects/{project_id}/priorities/'.format(project_id=project_id), data)
        priority_url = data['url']
        print priority_url

        status_urls = []
        data = {'name': 'New', 'description': "New", 'order': 0, 'is_initial': True}
        data, response = self.post('/projects/{project_id}/statuses/'.format(project_id=project_id), data)
        status_urls.append(data['url'])

        data = {'name': 'Done', 'description': "Done", 'order': 1, 'is_resolved': True}
        data, response = self.post('/projects/{project_id}/statuses/'.format(project_id=project_id), data)
        status_urls.append(data['url'])
        print status_urls

        data = {'name': 'Lovelace', 'description': "Steam punk without the '80s"}
        data, response = self.post('/projects/{project_id}/components/'.format(project_id=project_id), data)
        component_url = data['url']
        print component_url

        data = {'name': 'Milestone 1', 'description': "Milestone 1: Abney Park music"}
        data, response = self.post('/projects/{project_id}/milestones/'.format(project_id=project_id), data)
        milestone_url = data['url']
        print milestone_url

        count = 0

        tasks_data = [
            ('UV-map the roof', 'The roof has missing texture coordinates.'),
            ('Redo wall texture', 'The wall texture does not tile properly.'),
            ('Window edges have z-fighting', 'When looking from afar and at an angle the windows flicker.'),
        ]

        users_data = map(lambda x: '/users/'+str(x)+'/', User.objects.all().values_list('id', flat=True))
        users_data.insert(0, None)


        fileList = []
        directory = '../tempest-data'
        for root, subFolders, files in os.walk(directory):
            if '.svn' in subFolders:
                subFolders.remove('.svn')
            for file in files:
                #if file.endswith('.ai'):
                p = os.path.join(root,file)
                fileList.append( (p, p.replace(directory, ''), ) )

        for file, rel_file in fileList:
            user_data = users_data[count%len(users_data)]
            task_data = tasks_data[count%len(tasks_data)]
            status_url = status_urls[count%len(status_urls)]
            print task_data, user_data, status_url
            count += 1


            file_id = None
            file_url = None
            with open(file) as fp:
                data = {'path': os.path.dirname(rel_file), 'file': fp}
                data, response = self.post('/projects/{project_id}/upload/'.format(project_id=project_id), data)
                file_id = data['id']
                file_url = data['url']

            print file_id, file_url

            data, response = self.get('/files/{file_id}/assets/'.format(file_id=file_id))
            for asset in data['results']:
                asset_url = asset['url']

                data = {'summary': asset['subname']+': '+task_data[0], 'description': task_data[0],
                    'deadline': datetime.date.today() + datetime.timedelta(days=2),
                    'status': status_url,
                    'priority': priority_url,
                    'type': tasktype_url,
                    'milestone': milestone_url,
                    'component': component_url,
                    'objecttask_tasks': [asset_url],
                    }
                if user_data:
                    data['owner'] = user_data
                print data
                data, response = self.post('/projects/{project_id}/tasks/'.format(project_id=project_id), data)

                print data

                task_id = data['id']
                print task_id


                data, response = self.get('/projects/{project_id}/tasks/{task_id}'.format(project_id=project_id, task_id=task_id))
                #assert data['objecttask_tasks'][0]['content_object']['url'] == asset_url
