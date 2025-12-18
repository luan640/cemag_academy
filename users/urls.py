
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLogoutView,CustomLoginView
from django.conf.urls import handler404

handler404 = 'users.views.custom_404'

urlpatterns = [
    # path('signup/', SignUpView.as_view(), name='signup'),
    path('', CustomLoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('create-user/', views.add_user, name='create-user'),
    path('users/<int:pk>/edit/', views.edit_user, name='edit-user'),
    path('users/<int:pk>/toggle-active/', views.toggle_user_active, name='toggle-user-active'),
]
