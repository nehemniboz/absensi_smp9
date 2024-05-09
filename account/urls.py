from django.contrib.auth import views
from django.urls import path, reverse_lazy

urlpatterns = [
    path('login/', views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('password-change/', views.PasswordChangeView.as_view(
        template_name='password_change.html', success_url=reverse_lazy('login')), name='password_change'),
]
