from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),

    # Auth
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('employee/login/', views.employee_login_view, name='employee_login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin side
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/employees/add/', views.add_employee, name='add_employee'),
    path('admin/work/assign/', views.assign_work, name='assign_work'),
    path('admin/work/<int:pk>/edit/', views.edit_work, name='edit_work'),
    path('admin/notices/', views.notice_list, name='notice_list'),
    path('admin/notices/<int:pk>/approve/', views.approve_notice, name='approve_notice'),
    path('admin/notices/<int:pk>/reject/', views.reject_notice, name='reject_notice'),
    path('admin/attendance/', views.attendance_view, name='attendance_view'),

    # Employee side
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/work/', views.employee_work_list, name='employee_work'),
    path('employee/notice/request/', views.notice_request, name='notice_request'),
    path('employee/attendance/', views.employee_attendance_view, name='employee_attendance'),
]
