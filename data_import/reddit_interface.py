import praw
from django.conf import settings
import urllib2
from lxml import etree
from StringIO import StringIO
from data_import.models import Moderator, Subreddit, User
from django.utils import timezone


def get_moderators_by_subreddit(subreddit):
    user_agent = settings.REDDIT_USER_AGENT
    reddit = praw.Reddit(user_agent=user_agent)
    return reddit.get_subreddit(subreddit).get_moderators()


def store_moderators_for_subreddit(subreddit):
    mods = None
    try:
        mods = get_moderators_by_subreddit(subreddit)
    except Exception as e:
        print e
        raise
    if mods is not None:
        _store_moderators_for_subreddit(subreddit, mods)


def _store_moderators_for_subreddit(subreddit, mods):
    sub, sub_created = Subreddit.objects.get_or_create(name=subreddit)
    sub.mark_updated()

    mod_names = []
    for mod in mods:
        mod_names.append(mod.name)
    if not sub_created:
        # Remove users who are no longer moderators on a subreddit
        Moderator.objects.filter(is_deleted=False, subreddit__name=sub.name)\
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
    User.objects.bulk_create(user_objects)

    user_dict = {}
    mod_users = User.objects.filter(username__in=mod_names)
    for mod_user in mod_users:
        user_dict[mod_user.username] = mod_user

    mods_to_update = Moderator.objects.filter(subreddit=sub,
                                              user__username__in=mod_names)
    mods_to_update.update(last_updated=timezone.now())

    existing_mods = []
    for mod in mods_to_update:
        existing_mods.append(mod.user.username)

    mods_to_create = list(set(mod_names) - set(existing_mods))

    mod_objects = []
    for mod in mods_to_create:
        mod_objects.append(Moderator(subreddit=sub,
                                     user=user_dict[mod],
                                     last_updated=timezone.now()))
    Moderator.objects.bulk_create(mod_objects)


def get_modded_subs_by_user(user):
    user_doc = None
    try:
        user_doc = _get_user_profile(user)
    except urllib2.URLError, e:
        if e.code == 404:
            user.is_private = True
            user.last_updated = timezone.now()
            user.save()
    if user_doc is not None:
        _parse_user_profile(user, user_doc)

def _get_user_profile(user):
    hdr = {'User-Agent': settings.REDDIT_USER_AGENT}
    url = "http://www.reddit.com/user/%s" % user.username
    req = urllib2.Request(url, headers=hdr)
    return urllib2.urlopen(req).read()

def _parse_user_profile(user, html):
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser)

    table = tree.xpath("//ul[@id='side-mod-list']")
    rows = table[0].getchildren()
    subreddits = []

    for row in rows:
        li = row.getchildren()[0]
        subreddit = _clean_sub_name(li.text)
        subreddits.append(subreddit)
    existing_subs = Subreddit.objects.filter(name__in=subreddits)
    existing_subs.update(last_updated=timezone.now())

    existing_subs_names = []
    for existing_sub in existing_subs:
        existing_subs_names.append(existing_sub.name)

    sub_names_to_create = list(set(subreddits) - set(existing_subs_names))
    sub_objects = []
    for name in sub_names_to_create:
        sub_objects.append(Subreddit(name=name))
    Subreddit.objects.bulk_create(sub_objects)

    sub_dict = {}
    for subreddit_object in \
            Subreddit.objects.filter(name__in=subreddits):
        sub_dict[subreddit_object.name] = subreddit_object

    existing_modded_subs = \
        Moderator.objects.filter(user__username=user.username,
                                 subreddit__name__in=subreddits,
                                 is_deleted=False)
    existing_modded_subs.update(last_updated=timezone.now())

    existing_mod_sub_names = []
    for ems in existing_modded_subs:
        existing_mod_sub_names.append(ems.subreddit.name)

    mods_to_create = list(set(subreddits) - set(existing_mod_sub_names))
    mod_objs = []
    for mtc in mods_to_create:
        mod_objs.append(Moderator(user=user,
                                  subreddit=sub_dict[mtc],
                                  last_updated=timezone.now()))
    Moderator.objects.bulk_create(mod_objs)

    # Remove deleted mods
    removed_mods = Moderator.objects.filter(is_deleted=False,
                                            user__username=user.username)\
        .exclude(subreddit__name__in=subreddits)
    removed_mods.update(is_deleted=True, deleted_on=timezone.now())
    user.is_private = False
    user.mark_updated()


def _clean_sub_name(sub_text):
    return sub_text.replace('/r/', '')
