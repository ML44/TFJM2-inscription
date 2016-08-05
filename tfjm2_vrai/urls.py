from django.conf.urls import include, url, patterns
from django.contrib import admin

from django.conf.urls.static import static
from django.conf import settings


urlpatterns = patterns('',
	url(r'^$', 'inscription.views.home'),
	url(r'^', include('inscription.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<equipe>.*)/(?P<problemes>.*)/(?P<numero>.*)/(?P<version>.*)/(?P<url>.*)/(?P<filename>.*)$', 'inscription.views.private_ddl'),
    )

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)