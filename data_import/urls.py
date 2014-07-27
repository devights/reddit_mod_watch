from django.conf.urls import patterns, include, url
from data_import.views import sub_bar_chart, test_view, top_moderators, compare_subs

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', sub_bar_chart),
    url(r'^test', test_view),
    url(r'^top', top_moderators),
    url(r'^compare', compare_subs),
)
