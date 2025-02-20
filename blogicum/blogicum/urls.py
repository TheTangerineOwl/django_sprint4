"""blogicum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import PasswordResetConfirmView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


from blog.views import RegistrationView, PasswordResetEmailView


handler404 = 'pages.views.handle404'
handler500 = 'pages.views.handle500'
handler403csrf = 'pages.view.handle403csrf'


app_name = 'blogicum'

urlpatterns = [

    path('auth/password_reset/',
         PasswordResetEmailView.as_view(),
         name='password_reset'),
    path('auth/password_reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path(
        'auth/registration/',
        RegistrationView.as_view(),
        name='registration',
    ),
    path('auth/', include('django.contrib.auth.urls')),

    path('pages/', include('pages.urls')),
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
