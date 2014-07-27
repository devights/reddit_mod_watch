import praw
from django.conf import settings
from praw.errors import RedirectException
import urllib2
from lxml import etree
from StringIO import StringIO
from data_import.models import Moderator, Subreddit, User

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
    if not sub_created:
        #Remove users who are no longer moderators on a subreddit
        removed_mods = Moderator.objects.filter(is_deleted=False).exclude(user__username__in=mods)
        for removed_mod in removed_mods:
            removed_mod.undelete()

    for mod in mods:
        user, user_created = User.objects.get_or_create(username=mod)
        moderator, mod_created = Moderator.objects.get_or_create(user=user, subreddit=sub)
        if not mod_created:
            #Update last updated date
            moderator.save()


def get_modded_subs_by_user(user):
    username = user.username
    hdr = { 'User-Agent' : settings.REDDIT_USER_AGENT }
    url = "http://www.reddit.com/user/%s" % user.username
    req = urllib2.Request(url, headers=hdr)
    try:
        html = urllib2.urlopen(req).read()
    except Exception as ex:
        print ex
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
