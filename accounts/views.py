from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

# activation email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


#assigning items from guest cart to user cart.
from cart.views import get_cart
from cart.models import CartItem,Cart

# keeping the user flow
import requests
from orders.models import Order

# edit profile imports
from .forms import ProfileForm, AccountForm
from .models import UserProfile


def login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email, password=password)
        if user is not None:
            # gets the items from guest cart
            cart_guest=get_cart(request)
            try:
                cart_user=Cart.objects.get(user=user)
                items_guest=CartItem.objects.filter(cart=cart_guest)
                items_user=CartItem.objects.filter(cart=cart_user)
                for item_guest in items_guest:
                    item_added_in_cart=False
                    for item_user in items_user:
                        if (item_guest.product==item_user.product) and (set(item_guest.variation.all())==set(item_user.variation.all())):
                            item_user.quantity+=item_guest.quantity
                            item_user.save()
                            item_added_in_cart=True
                            break
                    if item_added_in_cart==False:
                        item_guest.cart=cart_user
                        item_guest.save()
                cart_guest.delete() 
            except Cart.DoesNotExist:
                cart_guest.user=user
                cart_guest.save()
            # login
            auth.login(request,user)

            url=request.META.get('HTTP_REFERER')
            try:
                query=requests.utils.urlparse(url).query
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    return redirect(params['next'])
            except:
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
        messages.success(request,'Congratulations! Your account has been Activated!.')
        return redirect('login_route')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register_route')

def forgot_password(request):
    if request.method=='POST':
        email=request.POST['email']
        try:
            user=Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request,f"account with email: {email} does not exist")
            return render(request, 'account/forgotPassword.html')
        current_site=get_current_site(request)
        to_email=user.email
        email_subject='Password Reset Link'
        email_message=render_to_string('account/email_passwordreset.html',{
            'user':user,
            'domain':current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user)
        })
        send_email=EmailMessage(email_subject, email_message, to=[to_email])
        send_email.send()
        messages.success(request,f'The Password Reset Link has been sent to your email: {email}')
        return render(request, 'account/login.html')
    return render(request,'account/forgotPassword.html')

def reset_password(request, uidb64, token):
    uid=urlsafe_base64_decode(uidb64).decode()
    try:
        user=Account.objects.get(pk=uid)
    except:
        user=None
    if user!=None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        return render(request,'account/resetpassword.html')
    else:
        messages.error(request,'Password Reset Link has expired')
        return render(request,'account/forgotPassword.html')

def reset_password(request):
    if request.method=='POST':
        password=request.POST['password']
        confirmpassword=request.POST['confirmpassword']
        if password!=confirmpassword:
            messages.error(request, 'Your Passwords Does Not Match')
            return render(request, 'account/resetpassword.html')
        uid=request.session['uid']
        if uid==None:
            return render(request, 'account/login.html')
        user=Account.objects.get(pk=uid)
        user.set_password(password)
        user.save()
        messages.success(request, 'Your password has been changed!')
        return render(request, 'account/login.html')

@login_required(login_url='login_route')
def dashboard(request):
    try:
        userprofile=UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        userprofile=UserProfile.objects.create(user=request.user)
    order_count=Order.objects.filter(user=request.user, is_ordered=True).count()
    return render(request, 'store/dashboard.html',{'order_count':order_count,'userprofile': userprofile,})

def orders_list(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    return render(request, 'store/orders_list.html', {'orders':orders})

def editprofile(request):
    try:
        userprofile=UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        userprofile=UserProfile.objects.create(user=request.user)
    if request.method=="POST":
        acc_form=AccountForm(request.POST, instance=request.user)
        prof_form=ProfileForm(request.POST, request.FILES, instance=userprofile)

        if acc_form.is_valid() and prof_form.is_valid():
            acc_form.save()
            prof_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('edit_profile_route')
        else:
            messages.error(request, 'Please correct the error below.')
            return redirect('edit_profile_route')
    else:
        acc_form=AccountForm(instance=request.user)
        prof_form=ProfileForm(instance=userprofile)
        context={
            'account_form': acc_form,
            'profile_form': prof_form,
            'userprofile': userprofile,
        }
        return render(request, 'store/profile_edit.html', context)
    
@login_required(login_url='login_route')
def change_password(request):
    if request.method=='POST':
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_new_password']
        user=Account.objects.get(email=request.user.email)
        if new_password==confirm_password:
            success=user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been updated successfully.')
                return redirect('change_password_route')
            else:
                messages.warning(request, 'Please enter valid current password.')
                return redirect('change_password_route')
        else:
            messages.warning(request, 'New password and confirm password does not match.')
            return redirect('change_password_route')
    return render(request, 'store/change_password.html')
    
