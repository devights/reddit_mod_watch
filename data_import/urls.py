from django.conf.urls import patterns, include, url
from data_import.views \
    import sub_bar_chart, test_view, top_moderators, compare_subs

urlpatterns = patterns('',
                       url(r'^$', sub_bar_chart),
                       url(r'^test', test_view),
                       url(r'^top', top_moderators),
                       url(r'^compare', compare_subs),
                       )
