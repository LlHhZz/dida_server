"""
URL configuration for didaxcx project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from didaxcx.views import wechat_login, user_info, modify_username, upload_story, find_story, collect_or_discollect_story, get_story_collected_state, get_collected_story, upload_question, get_answer, modify_roleinfo, get_all_story, modify_photo

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('token/', TokenObtainPairView.as_view(), name='settings_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='settings_token_refresh'),
    path('wechat/login/', wechat_login, name='wechat_login'),
    path('user/info/', user_info, name='user_info'),
    path('user/modify/username/', modify_username, name='modify_username'),
    path('user/modify/photo/', modify_photo, name='modify_photo'),
    path('upload/story/', upload_story, name='upload_story'),
    path('find/story/', find_story, name='find_story'),
    path('change/story/collected/', collect_or_discollect_story, name='collect_or_discollect_story'),
    path('get/story/collected/', get_story_collected_state, name='get_story_collected_state'),
    path('get/collected/story/', get_collected_story, name='get_collected_story'),
    path('upload/question/', upload_question, name='upload_question'),
    path('get/answer/', get_answer, name='get_answer'),
    path('user/modify/roleinfo/', modify_roleinfo, name='modify_roleinfo'),
    path('get/all/story/', get_all_story, name='get_all_story'),
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
]
