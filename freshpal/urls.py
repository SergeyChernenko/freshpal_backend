from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework_simplejwt import views as jwt_views

from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from freshpal import settings

urlpatterns = [
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/startpage/', include('startpage.urls')),
    path('api/mainpage/', include('mainpage.urls')),
    path('api/home/', include('home.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
