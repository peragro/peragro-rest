from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test import Client
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token


class UploadPaperTest(TestCase):

    def generate_file(self):
        try:
            myfile = open('test.csv', 'wb')
            wr = csv.writer(myfile)
            wr.writerow(('Paper ID','Paper Title', 'Authors'))
            wr.writerow(('1','Title1', 'Author1'))
            wr.writerow(('2','Title2', 'Author2'))
            wr.writerow(('3','Title3', 'Author3'))
        finally:
            myfile.close()

        return myfile

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
        token = Token.objects.create(user=self.user)
    
    def test_paper_upload(self):
        print Token.objects.all()
        token =  Token.objects.get(user_id = self.user.pk) # this outputs a normal looking token
        token_auth = self.client.post("/api-token-auth/", {'username': 'admin', 'password': 'admin'})
        print token_auth.data, token_auth.status_code # this outputs 400
        self.assertEqual(token_auth.status_code, 200, "User couldn't log in")
        
        
        response = self.client.login(username=self.user.username, password='admin')
        print('-'*70)
        print(response)
        print('-'*70)
        self.assertTrue(response)
        
        f = open("/home/sueastside/dev/DAMN/damn-test-files/image/jpg/crate10b.jpg", 'rb')
        
        post_data = {'file': None}
        #response = self.client.post(url, post_data)
        #self.assertContains(response, 'File type is not supported.')
        
        url = reverse('upload_file', args=['test_project'])
        print(url)

        post_data['file'] = f
        response = self.client.post(url, post_data, **{'HTTP_AUTHORIZATION':'Token '+token_auth.data['token'], })
        print(response)
        
        
    def ttest_paper_upload(self):
        response = self.client.login(username=self.user.email, password='foz')
        self.assertTrue(response)

        myfile = self.generate_file()
        file_path = myfile.name
        f = open(file_path, "r")

        url = reverse('registration_upload_papers', args=[self.event.slug])

        # post wrong data type
        post_data = {'uploaded_file': i}
        response = self.client.post(url, post_data)
        self.assertContains(response, 'File type is not supported.')

        post_data['uploaded_file'] = f
        response = self.client.post(url, post_data)

        import_file = SubmissionImportFile.objects.all()[0]
        self.assertEqual(SubmissionImportFile.objects.all().count(), 1)
        #self.assertEqual(import_file.uploaded_file.name, 'files/registration/{0}'.format(file_path))

        os.remove(myfile.name)
        file_path = import_file.uploaded_file.path
        os.remove(file_path)
