from django.conf.urls.defaults import *
import settings

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^', include('alipay_python.payment.urls')),
    # (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('alipay_python.accounts.urls')),                       
)
