from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.http import HttpResponse
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required


# Create your views here.
def login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email, password=password)
        print(user,email,password)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            messages.warning(request,'Invalid Credentials')
            return redirect('login_route')
    return render(request, 'account/login.html')


def register(request):
    if request.method=='POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=(email.split("@"))[0]
            user=Account.objects.create_user(username=username,password=password,first_name=first_name,last_name=last_name,email=email)
            messages.success(request,'Account Created Successfully')
            return redirect("login_route")
        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    messages.warning(request,error)
            return render(request, 'account/register.html',{'form':form})
    return render(request, 'account/register.html',{'form':RegistrationForm})

@login_required(login_url='login_route')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login_route')