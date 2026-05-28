from django.shortcuts import render
from django.contrib import messages
from users.forms import UserRegistrationForm
from users.models import UserRegistrationModel  # ✅ Ensure correct model import

# Admin Login View
def AdminLoginCheck(request):
    if request.method == 'POST':
        print("ADMIN POST DATA =", request.POST)

        usrid = request.POST.get('loginid', '').strip().lower()
        pswd = request.POST.get('pswd', '').strip()

        print("Admin Login ID is =", repr(usrid))
        print("Admin Password is =", repr(pswd))

        if usrid == 'admin' and pswd == 'admin':
            return render(request, 'admins/AdminHome.html')
        else:
            messages.error(request, 'Please check your login details.')

    return render(request, 'AdminLogin.html')

# Admin Home View
def AdminHome(request):
    return render(request, 'admins/AdminHome.html')

# View Registered Users
def RegisterUsersView(request):
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/viewregisterusers.html', {'data': data})

# Activate User
def activate_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('uid')
        
        try:
            user = UserRegistrationModel.objects.get(id=user_id)  # ✅ Correct model usage
            user.status = 'activated'
            user.save()
            messages.success(request, f'User {user.name} activated successfully!')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'User not found.')  # ✅ Handle case where user doesn't exist

    # Fetch updated user data
    data = UserRegistrationModel.objects.all()  # ✅ Fetch updated user list

    return render(request, 'admins/viewregisterusers.html', {'data': data})  # ✅ Correct template
