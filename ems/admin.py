from django.contrib import admin
from .models import Employee, WorkAssignment, Notice, Attendance

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'position', 'join_date')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'department')

@admin.register(WorkAssignment)
class WorkAssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'tasker', 'assigner', 'assign_date', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('title', 'tasker__employee_id', 'tasker__user__username')

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('subject', 'employee', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('subject', 'employee__employee_id', 'employee__user__username')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'remark')
    list_filter = ('status', 'date')
    search_fields = ('employee__employee_id', 'employee__user__username')
