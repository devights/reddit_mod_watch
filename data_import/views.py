from django.shortcuts import render
from data_import.models import Subreddit, User, Moderator
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import json
from collections import defaultdict

def sub_bar_chart(request):
    sub = request.GET.get('sub', None)
    if sub is None:
        return HttpResponse('error, missing sub')

    subreddit = Subreddit.objects.get(name=sub)
    moderators = Moderator.objects.filter(subreddit__id = subreddit.id)

    subreddit_mod_count = defaultdict(int)
    for mod in moderators:
        subs_moded_by_user = Moderator.objects.filter(user__id=mod.user.id).exclude(subreddit__id=subreddit.id)
        for sub_modded in subs_moded_by_user:
            subreddit_mod_count[sub_modded.subreddit.name] += 1


    labels = []
    values = []
    for key in subreddit_mod_count.iterkeys():
        if subreddit_mod_count[key] > 1:
            labels.append(key)
            values.append(subreddit_mod_count[key])

    values, labels = zip(*sorted(zip(values, labels), reverse=True))


    # return HttpResponse(json.dumps(subreddit_mod_count))
    return render_to_response('subreddit_bar.html',{'labels': labels,
                                                    'values': values})


def test_view(request):
    sub = request.GET.get('sub', None)
    user = request.GET.get('user', None)

    mods = Moderator.objects.all().order_by('subreddit__name')

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
    return render_to_response('test.html', {'mods':mod_output})