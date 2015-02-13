from django.conf.urls import patterns, url

urlpatterns = patterns(
    'dateoverride.views',
    url(r'override', 'override'),
)
