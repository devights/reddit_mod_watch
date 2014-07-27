from django.core.management.base import BaseCommand, CommandError
from data_import.reddit_interface import get_modded_subs_by_user, store_moderators_for_subreddit
from data_import.models import User, Subreddit
from datetime import datetime
from time import sleep

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        subs = Subreddit.objects.filter(last_updated=None)
        for sub in subs:
            start = datetime.now()
            store_moderators_for_subreddit(sub.name)
            time_taken = (datetime.now() - start).seconds
            if time_taken < 2:
                sleep(2-time_taken)

        users = User.objects.filter(last_updated=None)
        for user in users:
            if user.username == "AutoModerator":
                continue
            start = datetime.now()
            get_modded_subs_by_user(user)
            time_taken = (datetime.now() - start).seconds
            if time_taken < 2:
                sleep(2-time_taken)




