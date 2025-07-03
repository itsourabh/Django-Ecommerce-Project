from django.urls import path,include
from accounts import views
from accounts import views as accounts_views

urlpatterns = [
    # path('user_login', views.user_login, name="user_login"),
    path('user_login/', accounts_views.user_login, name='user_login'),
    path('user_register',accounts_views.user_register, name="user_register"),
    path('user_logout',accounts_views.user_logout, name="user_logout"),
    
]
