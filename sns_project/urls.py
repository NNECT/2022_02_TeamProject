"""sns_project URL Configuration

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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from sns_main import views
from django.contrib.auth import views as auth_views
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register'),
    path('user_info/', views.ModifyInfo.as_view(), name='modify'),
    path('', views.Timeline.as_view(), name='timeline'),
    path('feed/', views.TimelineFeed.as_view(), name='feed'),
    path('user/<str:username>/', views.TimelineUser.as_view(), name='timeline_user'),
    path('user/<str:username>/follow/', views.UserFollowList.as_view(), name='follow'),
    path('user/<str:username>/follower/', views.UserFollowerList.as_view(), name='follower'),
    path('tag/<int:pk>/', views.TimelineTag.as_view(), name='timeline_tag'),
    path('message/<int:pk>/', views.TimelineDetail.as_view(), name='timeline_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('search/user/<str:search_key>/', views.SearchUser.as_view(), name='search_user'),
    path('search/tag/<str:search_key>/', views.SearchTag.as_view(), name='search_tag'),

    path('following/', views.user_follow, name='user_follow'),
    path('like/', views.card_like, name='card_like'),
    path('forward/', views.card_forward, name='card_forward'),
    path('new_content/', views.load_new_content, name='new_content'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
