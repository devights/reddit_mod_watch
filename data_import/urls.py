from django.conf.urls import patterns, include, url
from data_import.views import sub_bar_chart, test_view

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', sub_bar_chart),
    url(r'^test', test_view),
)
