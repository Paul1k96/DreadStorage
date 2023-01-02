"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from core import settings
from crm.views import pageNotFound

urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/done/', auth_views
         .PasswordResetDoneView.as_view(template_name='crm/password/password_reset_done.html'),
         name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/', auth_views
         .PasswordResetConfirmView.as_view(template_name='crm/password/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset/complete/', auth_views
         .PasswordResetCompleteView.as_view(template_name='crm/password/password_reset_complete.html'),
         name='password_reset_complete'),
    path('', include('crm.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = pageNotFound
