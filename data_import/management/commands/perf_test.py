from django.core.management.base import BaseCommand
from data_import.reddit_interface import get_moderators_by_subreddit, _store_moderators_for_subreddit
from data_import.models import User, Subreddit, Moderator
from datetime import datetime
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Clean any existing data in the db
        User.objects.all().delete()
        Subreddit.objects.all().delete()
        sub_list = ["holocaust", "funny", "aww", "pics", "trains", "politics"]

        #Things to track
        sub_count = len(sub_list)
        mod_count = 0
        start_time = time.time()
        fetch_time = 0.0
        store_time = 0.0

        for sub in sub_list:
            #fetch mods
            fetch_start = time.time()
            mods = get_moderators_by_subreddit(sub)
            fetch_time += time.time() - fetch_start

            #Store mods
            store_start = time.time()
            _store_moderators_for_subreddit(sub, mods)
            store_time += time.time() - store_start
            mod_count += len(mods)

        end_time  = time.time() - start_time

        print "%s subs and %s mods in %s seconds" % (sub_count, mod_count, round(end_time, 4))
        print "average time per mod %s" % round(mod_count/end_time, 2)
        print "total fetch time: %s, %s per second" % (round(fetch_time, 4), round(sub_count/fetch_time, 2))
        print "total store time: %s, %s per second" % (round(store_time, 4), round(mod_count/store_time, 2))

        # store_moderators_for_subreddit("holocaust")

        # sub_start = datetime.now()
        # subs = Subreddit.objects.filter(last_updated=None)
        # for sub in subs:
        #     start = datetime.now()
        #     try:
        #         store_moderators_for_subreddit(sub.name)
        #     except Exception as ex:
        #         print ex
        #     time_taken = (datetime.now() - start).seconds
        #     if time_taken < 2:
        #         sleep(2-time_taken)
        # sub_time = (datetime.now() - sub_start).seconds
        # user_start = datetime.now()
        # users = User.objects.filter(last_updated=None)
        # for user in users:
        #     if user.username == "AutoModerator":
        #         continue
        #     start = datetime.now()
        #     try:
        #         get_modded_subs_by_user(user)
        #     except Exception as ex:
        #         print ex
        #     time_taken = (datetime.now() - start).seconds
        #     if time_taken < 2:
        #         sleep(2-time_taken)
        # user_time = (datetime.now() - user_start).seconds
        #
        # print "Added %s subs in %s seconds \nand %s users in %s seconds)"\
        #       % (len(subs), sub_time, len(users), user_time)
