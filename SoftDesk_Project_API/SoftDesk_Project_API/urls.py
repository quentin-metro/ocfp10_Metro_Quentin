"""
URL configuration for SoftDesk_Project_API project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from API.views import signup_view
from API.views import project_get_or_create, project_handler
from API.views import user_project_get_or_create, user_project_delete
from API.views import issue_get_or_create, issue_handler
from API.views import comment_get_or_create, comment_handler


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup_view, name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('projects/', project_get_or_create, name='projects'),
    path('projects/<int:project_id>/', project_handler, name='project_handler'),
    path('projects/<int:project_id>/users/', user_project_get_or_create, name='contributor'),
    path('projects/<int:project_id>/users/<int:user_id>', user_project_delete, name='contributor_delete'),
    path('projects/<int:project_id>/issues/', issue_get_or_create, name='issues'),
    path('projects/<int:project_id>/issues/<int:issue_id>/', issue_handler, name='issue_handler'),
    path('projects/<int:project_id>/issues/<int:issue_id>/comments/',
         comment_get_or_create, name='comments'
         ),
    path('projects/<int:project_id>/issues/<int:issue_id>/comments/<int:comment_id>',
         comment_handler, name='comment_handler'
         ),
]
