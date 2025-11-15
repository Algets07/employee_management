from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from .models import Employee, WorkAssignment, Notice, Attendance
from .forms import EmployeeCreateForm, WorkAssignmentForm, NoticeForm, AttendanceForm


def is_admin(user):
    return user.is_authenticated and user.is_staff


def is_employee(user):
    return user.is_authenticated and hasattr(user, 'employee') and not user.is_staff


def home_redirect(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        elif is_employee(request.user):
            return redirect('employee_dashboard')
    return redirect('employee_login')


def admin_login_view(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and is_admin(user):
            login(request, user)
            return redirect('admin_dashboard')
        messages.error(request, 'Invalid admin credentials')
    return render(request, 'auth/admin_login.html')


def employee_login_view(request):
    if request.user.is_authenticated and is_employee(request.user):
        return redirect('employee_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and is_employee(user):
            login(request, user)
            return redirect('employee_dashboard')
        messages.error(request, 'Invalid employee credentials')
    return render(request, 'auth/employee_login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('employee_login')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    employees = Employee.objects.select_related('user').all().order_by('employee_id')
    total_employees = employees.count()
    pending_notices = Notice.objects.filter(status='PENDING').count()
    total_tasks = WorkAssignment.objects.count()

    recent_assignments = WorkAssignment.objects.select_related('tasker__user').order_by('-assign_date')[:5]
    recent_notices = Notice.objects.select_related('employee__user').order_by('-created_at')[:5]

    context = {
        'employees': employees,
        'total_employees': total_employees,
        'pending_notices': pending_notices,
        'total_tasks': total_tasks,
        'recent_assignments': recent_assignments,
        'recent_notices': recent_notices,
    }
    return render(request, 'admin/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            email = form.cleaned_data.get('email', '')
            employee_id = form.cleaned_data['employee_id']
            department = form.cleaned_data['department']
            position = form.cleaned_data['position']
            join_date = form.cleaned_data['join_date']
            phone = form.cleaned_data.get('phone', '')

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            # employees are normal users, not staff
            user.is_staff = False
            user.save()

            Employee.objects.create(
                user=user,
                employee_id=employee_id,
                department=department,
                position=position,
                join_date=join_date,
                phone=phone,
            )

            messages.success(request, f"Employee {username} created successfully")
            return redirect('admin_dashboard')
    else:
        form = EmployeeCreateForm()

    return render(request, 'admin/add_employee.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def assign_work(request):
    if request.method == 'POST':
        form = WorkAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.assigner = request.user
            assignment.save()
            messages.success(request, "Work assigned successfully")
            return redirect('admin_dashboard')
    else:
        form = WorkAssignmentForm()
    return render(request, 'admin/assign_work.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def edit_work(request, pk):
    assignment = get_object_or_404(WorkAssignment, pk=pk)
    if request.method == 'POST':
        form = WorkAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Work updated successfully")
            return redirect('admin_dashboard')
    else:
        form = WorkAssignmentForm(instance=assignment)
    return render(request, 'admin/edit_work.html', {'form': form, 'assignment': assignment})


@login_required
@user_passes_test(is_admin)
def notice_list(request):
    notices = Notice.objects.select_related('employee__user').order_by('-created_at')
    return render(request, 'admin/notice_list.html', {'notices': notices})


@login_required
@user_passes_test(is_admin)
def approve_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.status = 'APPROVED'
    notice.save()
    messages.success(request, "Notice approved")
    return redirect('notice_list')


@login_required
@user_passes_test(is_admin)
def reject_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.status = 'REJECTED'
    notice.save()
    messages.success(request, "Notice rejected")
    return redirect('notice_list')


@login_required
@user_passes_test(is_admin)
def attendance_view(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            dt = form.cleaned_data['date']
            status = form.cleaned_data['status']
            remark = form.cleaned_data.get('remark', '')

            Attendance.objects.update_or_create(
                employee=employee,
                date=dt,
                defaults={'status': status, 'remark': remark},
            )
            messages.success(request, "Attendance saved")
            return redirect('attendance_view')
    else:
        form = AttendanceForm()

    records = Attendance.objects.select_related('employee__user').all()
    return render(request, 'admin/attendance.html', {'form': form, 'records': records})


@login_required
@user_passes_test(is_employee)
def employee_dashboard(request):
    employee = request.user.employee
    tasks = employee.tasks.order_by('-assign_date')[:5]
    attendance = employee.attendance_records.order_by('-date')[:10]

    context = {
        'employee': employee,
        'tasks': tasks,
        'attendance': attendance,
    }
    return render(request, 'employee/employee_dashboard.html', context)


@login_required
@user_passes_test(is_employee)
def employee_work_list(request):
    employee = request.user.employee

    # Handle status update
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')

        task = get_object_or_404(WorkAssignment, pk=task_id, tasker=employee)

        # Only accept valid statuses
        valid_statuses = dict(WorkAssignment.STATUS_CHOICES).keys()
        if new_status in valid_statuses:
            task.status = new_status
            task.save()
            messages.success(request, "Task status updated.")
        else:
            messages.error(request, "Invalid status selected.")

        return redirect('employee_work')

    # GET – just show tasks
    tasks = employee.tasks.order_by('-assign_date')
    status_choices = WorkAssignment.STATUS_CHOICES

    return render(
        request,
        'employee/employee_work_list.html',
        {'tasks': tasks, 'status_choices': status_choices},
    )


@login_required
@user_passes_test(is_employee)
def notice_request(request):
    employee = request.user.employee
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.employee = employee
            notice.status = 'PENDING'
            notice.save()
            messages.success(request, "Notice request submitted")
            return redirect('employee_dashboard')
    else:
        form = NoticeForm()
    return render(request, 'employee/notice_request.html', {'form': form})


@login_required
@user_passes_test(is_employee)
def employee_attendance_view(request):
    employee = request.user.employee
    records = employee.attendance_records.order_by('-date')
    return render(request, 'employee/employee_attendance.html', {'records': records})
