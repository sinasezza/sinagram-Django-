from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from . import models, forms, decorators


@decorators.logout_required
def signup_view(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, 'Account registered successfully')
            return redirect('users:login')
        else:
            print(f"form error : {form.errors.as_data()}")
            messages.error(request, 'error in form fields')
    else:
        form = forms.SignupForm()


    return render(request, 'users/signup_page.html', {'form': form})


# ======================================

@decorators.logout_required
def login_view(request):
    if request.method == 'POST' :
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request,user)
                    messages.success(request,'hello {}'.format(user.username))
                    return redirect('index') if models.UserProfile.objects.filter(user=user).exists() else redirect('users:create-profile')
                else:
                    messages.error(request,'user in not active')
                    return redirect('index')
            else :
                messages.error(request,'username or password is wrong')
                # form  = forms.LoginForm()
    else :
        form = forms.LoginForm()

    context = {
        'form' : form,
    }

    return render(request,'users/login_page.html', context)

# ======================================

@login_required(login_url='users:login')
def Logout_view(request):
    logout(request)
    return redirect('users:login')

# ======================================

@login_required(login_url='users:login')
def create_profile_view(request):
    try:
        profile = models.UserProfile.objects.get(user=request.user)
    except:
        profile = None
        
    if request.method == 'POST':
        form = forms.UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request,"Your Profile has been created")
            return redirect('index')
        else:
            messages.error(request, "Please correct the error below.")
    else:            
        form = forms.UserProfileForm(instance=profile)
        
    context = {
        'form': form,
    }
    
    return render(request,  'users/create_profile.html', context)

# ======================================

# @login_required
# def profile_view(request, username):
#     user = get_object_or_404(User, username=username)
#     followers = user.followers.all().count()
#     following = user.following.all().count()

# ======================================

@login_required(login_url='users:login')
@decorators.profile_required
def panel_view(request, username = None):
    if not username:
        profile = models.UserProfile.objects.get(user=request.user)
        user = request.user
    else:
        profile = get_object_or_404(models.UserProfile, user__username=username)
        user = get_object_or_404(User, username=username)

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request,'users/panel.html',context)

# ======================================

@login_required(login_url='users:login')
@decorators.profile_required
def change_account_info_view(request):
    user_profile = models.UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        account_form = forms.AccountChangeForm(request.POST, instance=request.user)
        profile_form = forms.ProfileChangeForm(request.POST, request.FILES, instance=user_profile)
        if account_form.is_valid() and profile_form.is_valid():
            updated_account = account_form.save()
            updated_profile = profile_form.save()
            messages.success(request, 'Updated successfully')
            return redirect(user_profile.get_panel_url())
        else:
            print(f'account form errors : {account_form.errors.as_data()}')
            print(f'profile form errors : {profile_form.errors.as_data()}')
            messages.error(request, 'Form is not valid')
    else:
        account_form = forms.AccountChangeForm(instance=request.user)
        profile_form = forms.ProfileChangeForm(instance=user_profile)
        
    context = {
        'account_form': account_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/change_account_info.html', context)

# ======================================

@login_required(login_url='messenger:main_page')
def delete_user_view(request,username):
    account = models.Account.objects.get(user__exact = request.user)
    if request.method == "POST":
        form = forms.DeleteUserForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['yes'] == '1' :
                User.objects.get(username__exact=username).delete()
                messages.success(request,'account deleted successfully')
                return redirect('messenger:main_page')
            else:
                messages.error(request, 'the account deletion failed , please try again ...')
                return reverse_lazy(account.get_panel_url())
        else:
            messages.error(request,'form is not valid')
            return redirect('messenger:delete_user',request.user.username)
    else:
        form = forms.DeleteUserForm()
    
    context = {
        'form':form,
        'usr' : account,

    }
    return render(request,'forms/delete_user_form.html',context)

# ======================================

@login_required(login_url= 'users:login')
@decorators.profile_required
def contact_list_view(request):
    profile = models.UserProfile.objects.get(user=request.user)
    contacts = profile.my_contacts.all()
    context = {
        'profile': profile,
        'contacts':contacts,
    }
    return render(request,'users/contact_list.html',context)
 
# ======================================

@login_required(login_url='users:login')
@decorators.profile_required
def contact_detail_view(request, id):
    contact = get_object_or_404(models.Contact, id=id)
    
    try:
        contact_account = models.Account.objects.get(user_phone_number__exact = contact.phone_number)
        context = {
            'contact':contact,
            'account':contact_account,
        }
        
    except:
        context = {
            'contact':contact,
        }
        
    
    return render(request,'users/contact_detail.html',context) 
        
# ======================================

@login_required(login_url= 'users:login')
@decorators.profile_required
def add_contact_view(request):
    profile = models.UserProfile.objects.get(user__exact = request.user)
    if request.method == 'POST':
        form = forms.ContactAddForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.contact_saver = profile

            # assign profile to contact if exist
            try:
                contact_profile = models.UserProfile.objects.get(Q(phone=contact.phone) | Q(email=contact.email))
                contact.profile = contact_profile
            except:
                pass
            
            contact.save()
            messages.success(request,'the contact added successfully')
            return redirect('users:contact-list')
        else:
            print(f"form errors : {form.errors.as_data()}")
            messages.error(request,'the form is invalid')
    else:
        form = forms.ContactAddForm()
    
    context = {
        'form': form,
        'profile': profile,
    }
        
    return render(request, 'users/add_contact_page.html', context)

# ======================================

@login_required(login_url= 'users:login')
@decorators.profile_required
@decorators.contact_saver_required
def change_contact_info_view(request, id):
    contact = get_object_or_404(models.Contact, id=id)

    if request.method == 'POST':
        form = forms.ContactUpdateForm(data=request.POST, files=request.FILES, instance=contact)
        if form.is_valid():
            updated_contact = form.save()

            # assign profile to contact if exist
            contact_profile = models.UserProfile.objects.filter(Q(phone_number=updated_contact.phone)).distinct()
            if contact_profile.exists():
                updated_contact.profile = contact_profile.first()
                updated_contact.save()
            
            messages.success(request,'the contact Information Updated')
            return redirect(updated_contact.get_absolute_url())
        else :
            print(f"form error : {form.errors.as_data()}")
            messages.error(request,'the form is not valid')      
    else:
        form = forms.ContactUpdateForm(instance=contact)
        
    print(f"form is {form}")

    
    context = {
        'form':form,
        'contact': contact,
    }
    return render(request=request, template_name='users/change_contact_info.html', context=context)

# ======================================

@login_required(login_url= 'users:login')
@decorators.profile_required
def delete_contact_view(request, id):
    contact = get_object_or_404(models.Contact, id=id)
    
    if request.method == 'POST':
        form = forms.DeleteContactForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('yes') == '1':
                contact.delete()
                messages.success(request,'the contact deleted ...')
                return redirect('users:contact-list')
            else:
                messages.error(request,'the contact deletion failed , try again')
        else :
            messages.error(request,'the form is not valid')
    else:
        form = forms.DeleteContactForm()
    
    context = {
        'form':form,
        'contact':contact,
    }
    return render(request, 'users/delete_contact_form.html', context)
