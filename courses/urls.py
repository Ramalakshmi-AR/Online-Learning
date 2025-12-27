from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/feedback/', views.add_feedback, name='add_feedback'),
    path('buy/<int:course_id>/', views.buy_course, name='buy_course'),
    path('payment-success/', views.payment_success, name='payment_success'),
    


]
