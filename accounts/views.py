from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.http import HttpResponse
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

# activation email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


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

            # activation email process
            current_site=get_current_site(request)
            email_subject='Please activate your account'
            email_message=render_to_string('account/email_verification.html', {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email=email
            send_email=EmailMessage(email_subject, email_message, to=[to_email])
            send_email.send()

            messages.success(request,'An activation link has been sent to your email address. Please verify to complete the registration.')
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

def activate(request, uidb64, token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulations! Your account is activated.')
        return redirect('login_route')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register_route')