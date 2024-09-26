
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLogoutView
from django.conf.urls import handler404

handler404 = 'users.views.custom_404'

urlpatterns = [
    # path('signup/', SignUpView.as_view(), name='signup'),
    path('', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('create-user/', views.add_user, name='create-user'),
]