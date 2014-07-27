import praw
from django.conf import settings
from praw.errors import RedirectException
import urllib2
from lxml import etree
from StringIO import StringIO
from data_import.models import Moderator, Subreddit, User
from django.utils import timezone

from datetime import datetime

def get_moderators_by_subreddit(subreddit):
    user_agent = settings.REDDIT_USER_AGENT
    reddit = praw.Reddit(user_agent=user_agent)
    return reddit.get_subreddit(subreddit).get_moderators()

def store_moderators_for_subreddit(subreddit):
    try:
        mods = get_moderators_by_subreddit(subreddit)
    except Exception as e:
        print e
        raise
    sub, sub_created = Subreddit.objects.get_or_create(name=subreddit)
    sub.mark_updated()

    mod_names = []
    for mod in mods:
        mod_names.append(mod.name)
    if not sub_created:
        #Remove users who are no longer moderators on a subreddit
        removed_mods = Moderator.objects.filter(is_deleted=False, subreddit__name=sub.name)\
            .exclude(user__username__in=mod_names)\
            .update(is_deleted=True, deleted_on=timezone.now())

    users_to_update = User.objects.filter(username__in=mod_names)
    update_usernames = []
    for user in users_to_update:
        update_usernames.append(user.username)
    users_to_create = list(set(mod_names) - set(update_usernames))

    user_objects = []
    for user in users_to_create:
        user_obj = User(username=user)
        user_objects.append(user_obj)
        # user_dict[user_obj.username] = user_obj
    User.objects.bulk_create(user_objects)

    user_dict = {}
    mod_users = User.objects.filter(username__in=mod_names)
    for mod_user in mod_users:
        user_dict[mod_user.username] = mod_user

    mods_to_update = Moderator.objects.filter(subreddit=sub, user__username__in=mod_names)
    mods_to_update.update(last_updated=timezone.now())

    existing_mods = []
    for mod in mods_to_update:
        existing_mods.append(mod.user.username)

    mods_to_create = list(set(mod_names) - set(existing_mods))

    mod_objects = []
    for mod in mods_to_create:
        mod_objects.append(Moderator(subreddit=sub, user=user_dict[mod], last_updated=timezone.now()))
    Moderator.objects.bulk_create(mod_objects)


def get_modded_subs_by_user(user):
    username = user.username
    hdr = { 'User-Agent' : settings.REDDIT_USER_AGENT }
    url = "http://www.reddit.com/user/%s" % user.username
    req = urllib2.Request(url, headers=hdr)
    try:
        html = urllib2.urlopen(req).read()
    except Exception as ex:
        print ex
        print url
        raise

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser)

    table = tree.xpath("//ul[@id='side-mod-list']")
    rows = table[0].getchildren()
    subreddits = []

    for row in rows:
        li = row.getchildren()[0]
        subreddit = _clean_sub_name(li.text)
        subreddits.append(subreddit)

        sub, sub_created = Subreddit.objects.get_or_create(name=subreddit)
        try:
            moderator = Moderator.objects.get(user_id=user.id, subreddit_id=sub.id)
            moderator.save()
            if moderator.is_deleted:
                moderator.undelete()
        except Moderator.DoesNotExist:
            mod = Moderator(user=user, subreddit=sub)
            mod.save()


    #Remove deleted mods
    removed_mods = Moderator.objects.filter(is_deleted=False, user__username=username).exclude(subreddit__name__in=subreddits)
    for removed_mod in removed_mods:
        list = ", ".join(subreddits)
        removed_mod.mark_deleted()
    user.mark_updated()

def _clean_sub_name(sub_text):
    return sub_text.replace('/r/', '')
