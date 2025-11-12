from django.conf import settings
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('store/', include('store.urls')),
] + debug_toolbar_urls()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('_debug_/', include(debug_toolbar.urls)),
    ] + urlpatterns

from django.urls import re_path
import store.views

urlpatterns = [
    re_path(r'^$', store.views.index, name='index'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("_debug_/", include(debug_toolbar.urls))] + urlpatterns


