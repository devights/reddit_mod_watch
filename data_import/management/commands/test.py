from django.core.management.base import BaseCommand
from data_import.reddit_interface \
    import get_modded_subs_by_user, store_moderators_for_subreddit
from data_import.models import User, Subreddit
from datetime import datetime
from time import sleep


class Command(BaseCommand):
    def handle(self, *args, **options):
        store_moderators_for_subreddit("holocaust")
        sub_start = datetime.now()
        subs = Subreddit.objects.filter(last_updated=None)
        for sub in subs:
            start = datetime.now()
            try:
                store_moderators_for_subreddit(sub.name)
            except Exception as ex:
                print ex
            time_taken = (datetime.now() - start).seconds
            if time_taken < 2:
                sleep(2-time_taken)
        sub_time = (datetime.now() - sub_start).seconds
        user_start = datetime.now()
        users = User.objects.filter(last_updated=None)
        for user in users:
            if user.username == "AutoModerator":
                continue
            start = datetime.now()
            try:
                get_modded_subs_by_user(user)
            except Exception as ex:
                print ex
            time_taken = (datetime.now() - start).seconds
            if time_taken < 2:
                sleep(2-time_taken)
        user_time = (datetime.now() - user_start).seconds

        print "Added %s subs in %s seconds \nand %s users in %s seconds)"\
              % (len(subs), sub_time, len(users), user_time)
