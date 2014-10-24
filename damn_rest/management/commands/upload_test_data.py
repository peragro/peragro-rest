from django.core.management.base import BaseCommand, CommandError
from django.test.client import Client


class Command(BaseCommand):
    help = 'Upload test data set'

    def handle(self, *args, **options):
        print 'uploading...'
