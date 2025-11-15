from django import forms
from django.contrib.auth.models import User
from .models import WorkAssignment, Notice, Attendance, Employee

class EmployeeCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    employee_id = forms.CharField(max_length=20)
    department = forms.CharField(max_length=100)
    position = forms.CharField(max_length=100)
    join_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=20, required=False)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def clean_employee_id(self):
        emp_id = self.cleaned_data['employee_id']
        if Employee.objects.filter(employee_id=emp_id).exists():
            raise forms.ValidationError("Employee ID already exists")
        return emp_id

class WorkAssignmentForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = WorkAssignment
        fields = ['tasker', 'title', 'description', 'due_date']

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['subject', 'message']

class AttendanceForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status', 'remark']
