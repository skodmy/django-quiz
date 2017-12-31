from django.conf.urls import url, include
from .views import TestListView, TestDetailView, PassTestView, examine

urlpatterns = [
    url(r'^$', TestListView.as_view(), name='tests-list'),
    url(r'^test/', include([
        url(r'^(?P<test_pk>\d+)/', include([
            url(r'^$', TestDetailView.as_view(), name='test-detail'),
            url(r'^pass/', include([
                url(r'^$', PassTestView.as_view(), name='test-pass'),
                url(r'^result/$', examine, name='test-examine'),
            ])),
        ]))
    ]))
]
