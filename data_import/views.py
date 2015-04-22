from __future__ import division
from data_import.models import Subreddit, User, Moderator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from collections import defaultdict
from django.db.models import Count


def sub_bar_chart(request):
    sub = request.GET.get('sub', None)
    if sub is None:
        return HttpResponse('error, missing sub')

    subreddit = Subreddit.objects.get(name=sub)
    moderators = Moderator.objects.filter(subreddit__id=subreddit.id)

    subreddit_mod_count = defaultdict(int)
    for mod in moderators:
        subs_moded_by_user = Moderator.objects.filter(user__id=mod.user.id)\
            .exclude(subreddit__id=subreddit.id)
        for sub_modded in subs_moded_by_user:
            subreddit_mod_count[sub_modded.subreddit.name] += 1

    labels = []
    values = []
    for key in subreddit_mod_count.iterkeys():
        if subreddit_mod_count[key] > 1:
            labels.append(key)
            values.append(subreddit_mod_count[key])

    values, labels = zip(*sorted(zip(values, labels), reverse=True))

    return render_to_response('subreddit_bar.html', {'labels': labels,
                                                     'values': values})


def top_moderators(request):
    fetch_count = request.GET.get('count', 10)
    mods = Moderator.objects.all().values('user__username')\
        .annotate(total=Count('user__username'))\
        .order_by('-total')[:fetch_count]
    return render_to_response('top_mods.html', {'mods': mods})


def compare_subs(request):
    sub_1 = request.GET.get('sub1', None)
    sub_2 = request.GET.get('sub2', None)

    try:
        sub_1 = Subreddit.objects.get(name=sub_1)
        sub_2 = Subreddit.objects.get(name=sub_2)

        sub1_mods = []
        sub2_mods = []
        for mod in Moderator.objects.filter(subreddit=sub_1):
            sub1_mods.append(mod.user.username)
        for mod in Moderator.objects.filter(subreddit=sub_2):
            sub2_mods.append(mod.user.username)

        similar = set(sub1_mods).intersection(set(sub2_mods))
        sub1_percent = round(((len(similar) / len(sub1_mods)) * 100), 2)
        sub2_percent = round(((len(similar) / len(sub2_mods)) * 100), 2)
        data = {'similar_count': len(similar),
                'sub1_name': sub_1.name,
                'sub1_mod_count': len(sub1_mods),
                'sub1_percent': sub1_percent,
                'sub2_name': sub_2.name,
                'sub2_mod_count': len(sub2_mods),
                'sub2_percent': sub2_percent}
        return render_to_response('compare_subs.html', data)
    except Exception:
        return HttpResponseBadRequest()


def test_view(request):
    sub = request.GET.get('sub', None)
    user = request.GET.get('user', None)

    mods = Moderator.objects.all().order_by('user__username')

    if sub is not None:
        mods.filter(subreddit__name=sub)
    if user is not None:
        mods.filter(user__username=user)

    mod_output = []

    for mod in mods:
        mod_rep = {'subreddit': mod.subreddit.name,
                   'user': mod.user.username,
                   'added': str(mod.added_on),
                   'updated': str(mod.last_updated),
                   'is_deleted': mod.is_deleted,
                   'deleted': str(mod.deleted_on)}
        mod_output.append(mod_rep)
    return render_to_response('test.html', {'mods': mod_output})
