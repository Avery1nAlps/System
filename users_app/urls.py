from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'  # 命名空间，避免URL冲突

urlpatterns = [
    # 自定义登录页
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # 登出页（登出后跳回登录页）
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'),
    # 新增：临时首页路由
    path('home/', views.home, name='home'),
]