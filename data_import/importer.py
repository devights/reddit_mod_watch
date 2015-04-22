from data_import.reddit_interface import get_modded_subs_by_user, \
    store_moderators_for_subreddit
from data_import.models import User, Subreddit, Moderator
from django.conf import settings
import logging
import time
error_log = logging.getLogger('import_error')


def priority_import_user_subs(batch_limit):
    seed_if_needed()

    user_list = User.objects.all().order_by('-priority')[:batch_limit]

    rate_limit = getattr(settings, 'RATE_LIMIT_SECONDS', 2)
    for user in user_list:
        start = time.time()
        try:
            get_modded_subs_by_user(user)
        except Exception as ex:
            error_log.exception(ex)

        time_taken = time.time() - start
        if time_taken < rate_limit:
            time.sleep(rate_limit - time_taken)


def priority_import_sub_mods(batch_limit):
    seed_if_needed()
    sub_list = Subreddit.objects.all().order_by('-priority')[:batch_limit]

    # praw will handle rate limiting here
    for sub in sub_list:
        try:
            store_moderators_for_subreddit(sub.name)
        except Exception as ex:
            error_log.exception(ex)


def seed_if_needed():
    if not is_seeded():
        seed_database()


def is_seeded():
    modcount = Moderator.objects.all().count()
    return modcount > 0


def seed_database():
    seed_sub = getattr(settings, 'SEED_SUB', 'funny')
    try:
        store_moderators_for_subreddit(seed_sub)
    except Exception as ex:
        error_log.exception(ex)
