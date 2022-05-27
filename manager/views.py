from manager.decorators import unauthenticated_user,allowed_users
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Oders,ExtendedAuthUser,OrderFields,UserFileUploads
from django.contrib.auth.models import User,Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render,get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse,HttpResponse
from installation.models import SiteConstants
from django.shortcuts import redirect
from .forms import *
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from .addons import send_email,getSiteData
import json
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
import re
from .search import *
import datetime
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaulttags import register


@method_decorator(unauthenticated_user,name='dispatch')
class Dashboard(View):
    def get(self,request):
        obj=SiteConstants.objects.all()[0]
        data={
            'title':'Login',
            'obj':obj
        }
        return render(request,'manager/login.html',context=data)
    def post(self,request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            key=request.POST['username']
            password=request.POST['password']
            if key:
                if password:
                    regex=re.compile(r'([A-Za-z0-9+[.-_]])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
                    if re.fullmatch(regex,key):
                        #email address
                        if User.objects.filter(email=key).exists():
                            data=User.objects.get(email=key)
                            user=authenticate(username=data.username,password=password)
                        else:
                            form_errors={"username": ["Invalid email address."]}
                            return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                    else:
                        #username
                        if User.objects.filter(username=key).exists():
                            user=authenticate(username=key,password=password)
                        else:
                            form_errors={"username": ["Invalid username."]}
                            return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                        
                    if user is not None:
                        if 'remember' in request.POST:
                           request.session.set_expiry(1209600) #two weeeks
                        else:
                           request.session.set_expiry(0) 
                        login(request,user)
                        return JsonResponse({'valid':True,'feedback':'success:login successfully.'},content_type="application/json")
                    form_errors={"password": ["Password is incorrect or inactive account."]}
                    return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                else:
                    form_errors={"password": ["Password is required."]}
                    return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
            else:
                form_errors={"username": ["Username is required."]}
                return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")


@login_required(login_url='/')
def home(request):
    obj=SiteConstants.objects.all()[0]
    users_count=User.objects.count()
    orders_count=Oders.objects.count()
    completed_orders=OrderFields.objects.filter(status__icontains='delivered').count()
    cancelled_orders=OrderFields.objects.filter(status__icontains='cancelled').count()
    orders=OrderFields.objects.all().order_by('-modified_at')[:12]
    data={
        'title':'home',
        'obj':obj,
        'data':request.user,
        'users_count':users_count,
        'orders_count':orders_count,
        'completed_orders':completed_orders,
        'cancelled_orders':cancelled_orders,
        'orders':orders
    }
    return render(request,'manager/home.html',context=data)

#logout
def user_logout(request):
    logout(request)
    return redirect('/')

#newUser
@method_decorator(login_required(login_url='/'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class newUser(View):
    def get(self,request):
        obj=SiteConstants.objects.all()[0]
        form=users_registerForm()
        eform=EProfileForm()
        data={
            'title':'Add new user',
            'obj':obj,
            'data':request.user,
            'form':form,
            'eform':eform
        }
        return render(request,'manager/new_user.html',context=data)
    def post(self,request,*args,**kwargs):
        if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
                uform=users_registerForm(request.POST or None)
                eform=EProfileForm(request.POST , request.FILES or None)
                if uform.is_valid() and  eform.is_valid():
                    userme=uform.save(commit=False)
                    userme.is_active = True
                    userme.save()
                    extended=eform.save(commit=False)
                    extended.user=userme
                    extended.initials=uform.cleaned_data.get('first_name')[0].upper()+uform.cleaned_data.get('last_name')[0].upper()
                    extended.save()
                    user=User.objects.get(email__exact=uform.cleaned_data.get('email'))
                    ct=ContentType.objects.get_for_model(ExtendedAuthUser)
                    role=eform.cleaned_data.get('role')
                    if 'Secondary' in role:
                        if not Group.objects.filter(name='secondary').exists():
                            group=Group.objects.create(name='secondary')
                            group.user_set.add(userme)
                            p1=Permission.objects.filter(content_type=ct).all()[0]
                            p3=Permission.objects.filter(content_type=ct).all()[2]
                            group.permissions.add(p1)
                            group.permissions.add(p3)
                            group.save()
                        else:
                            group=Group.objects.get(name__icontains='secondary')
                            group.user_set.add(userme)
                            group.save()
                    elif 'Tertiary' in role:
                        if not Group.objects.filter(name='tertiary').exists():
                            group=Group.objects.create(name='tertiary')
                            group.user_set.add(userme)
                            p3=Permission.objects.filter(content_type=ct).all()[2]
                            group.permissions.add(p3)
                            group.save()
                        else:
                            group=Group.objects.get(name__icontains='tertiary')
                            group.user_set.add(userme)
                            group.save()
                    return JsonResponse({'valid':True,'message':'user added successfully','profile_pic':user.extendedauthuser.profile_pic.url},content_type="application/json")
                else:
                    return JsonResponse({'valid':False,'uform_errors':uform.errors,'eform_errors':eform.errors},content_type="application/json")

#viewUsers
@login_required(login_url='/')
@allowed_users(allowed_roles=['admins'])
def viewUsers(request):
    obj=SiteConstants.objects.all()[0]
    data=User.objects.all().order_by('-id')
    paginator=Paginator(data,10)
    page_num=request.GET.get('page')
    users=paginator.get_page(page_num)
    data={
        'title':'View users',
        'obj':obj,
        'data':request.user,
        'users':users,
        'count':paginator.count,
    }
    return render(request,'manager/view_users.html',context=data)

#edit user
@method_decorator(login_required(login_url='/'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class EditUser(View):
    def get(self,request,id):
        obj=SiteConstants.objects.all()[0]
        user=User.objects.get(extendedauthuser__user_id__exact=id)
        form=UserProfileChangeForm(instance=user)
        eform=ExtendedUserProfileChangeForm(instance=user.extendedauthuser)
        data={
            'title':f'Edit user | {user.first_name}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'eform':eform,
            'editor':user
        }
        return render(request,'manager/edit_user.html',context=data)
    def post(self,request,id,*args ,**kwargs):
        user=User.objects.get(extendedauthuser__user_id__exact=id)
        form=UserProfileChangeForm(request.POST or None,instance=user)
        eform=ExtendedUserProfileChangeForm(request.POST,request.FILES or None,instance=user.extendedauthuser)
        if form.is_valid() and eform.is_valid():
            form.save()
            eform.save()
            return JsonResponse({'valid':True,'message':'data saved'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors,'eform_errors':eform.errors,},content_type='application/json')

#delete user
@login_required(login_url='/')
@allowed_users(allowed_roles=['admins'])
def deleteUser(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=User.objects.get(id=id)
            obj.delete() 
            return JsonResponse({'valid':False,'message':'User deleted successfully.','id':id},content_type='application/json')       
        except User.DoesNotExist:
            return JsonResponse({'valid':True,'message':'User does not exist'},content_type='application/json')


#ProfileView
@method_decorator(login_required(login_url='/'),name='dispatch')
class ProfileView(View):
    def get(self,request,username):
        obj=SiteConstants.objects.all()[0]
        try:
            user=User.objects.get(username__exact=username)
            form=CurrentUserProfileChangeForm(instance=user)
            passform=UserPasswordChangeForm()
            eform=CurrentExtendedUserProfileChangeForm(instance=user.extendedauthuser)
            if request.user.is_superuser:
                eform.fields['role'].choices=[('Admin','View | Edit | Admin'),]
                eform.fields['role'].initial=[0]
            else:
                eform.fields['role'].choices=[('Tertiary','View only'),('Secondary','View | Edit'),('Admin','View | Edit | Admin'),]
                eform.fields['role'].initial=[0]
            data={
                'title':f'Edit profile | {user.first_name}',
                'obj':obj,
                'data':request.user,
                'form':form,
                'eform':eform,
                'editor':user,
                'passform':passform
            }
            return render(request,'manager/profile.html',context=data)
        except User.DoesNotExist:
            return render(request,'manager/404.html',{'title':'Error | Bad Request'},status=400)
 
    def post(self,request,username,*args ,**kwargs):
        form=UserProfileChangeForm(request.POST or None,instance=request.user)
        eform=ExtendedUserProfileChangeForm(request.POST,request.FILES or None,instance=request.user.extendedauthuser)
        if form.is_valid() and eform.is_valid():
            form.save()
            eform.save()
            return JsonResponse({'valid':True,'message':'data saved'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors,'eform_errors':eform.errors,},content_type='application/json')


#passwordChange
@login_required(login_url='/')
def passwordChange(request):
    if request.method=='POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        passform=UserPasswordChangeForm(request.POST or None,instance=request.user)
        if passform.is_valid():
            user=User.objects.get(username__exact=request.user.username)
            user.password=make_password(passform.cleaned_data.get('password1'))
            user.save()
            update_session_auth_hash(request,request.user)
            return JsonResponse({'valid':True,'message':'data saved'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'passform_errors':passform.errors},content_type='application/json')

#NewOrder
@method_decorator(login_required(login_url='/'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins','secondary']),name='dispatch')
class UserNewOrder(View):
    def get(self,request):
        obj=SiteConstants.objects.all()[0]
        orders=Oders.objects.all()
        form=NewOderForm()
        data={
                'title':'Create new order',
                'obj':obj,
                'data':request.user,
                'form':form,
                'orders':orders
            }
        return render(request,'manager/new_order.html',context=data)
    def post(self,request):
        form=NewOderForm(request.POST or None)
        if form.is_valid():
            form.save()
            order_id=OrderFields.objects.latest('id').id
            return JsonResponse({'valid':True,'message':'data saved','order_id':order_id},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'form_errors':form.errors},content_type='application/json')



#view orders
@login_required(login_url='/')
def viewOrders(request):
    obj=SiteConstants.objects.all()[0]
    data=Oders.objects.all().order_by('-ordername_id')
    paginator=Paginator(data,30)
    page_num=request.GET.get('page')
    orders=paginator.get_page(page_num)
    data={
        'title':'View orders',
        'obj':obj,
        'data':request.user,
        'orders':orders,
        'count':paginator.count,
    }
    return render(request,'manager/view_order.html',context=data)

#editMainOrder
@login_required(login_url='/')
@allowed_users(allowed_roles=['admins'])
def editMainOrder(request,id):
    data=Oders.objects.get(ordername_id=id)
    form=NewOderForm(request.POST or None,instance=data)
    if form.is_valid():
        form.save()
        return JsonResponse({'valid':True,'message':'data saved'},content_type='application/json')
    else:
        return JsonResponse({'valid':False,'form_errors':form.errors},content_type='application/json')



#editOrder
@method_decorator(login_required(login_url='/'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins','secondary']),name='dispatch')
class EditOrder(View):
    def get(self,request,id):
        obj=SiteConstants.objects.all()[0]
        data=OrderFields.objects.get(id=id)
        obj=Oders.objects.get(ordername_id=data.order_id)
        form=OrderFieldsForm(instance=data)
        customers=OrderFields.objects.all()
        data={
            'title':f'Edit oreder | {obj.ordername}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'editor':obj,
            'form_id':id,
            'customerlist':customers
        }
        return render(request,'manager/tabulate.html',context=data)
    def post(self,request,id):
        data=OrderFields.objects.get(id=id)
        form=OrderFieldsForm(request.POST,request.FILES or None,instance=data)
        if form.is_valid():
            t=form.save(commit=False)
            t.modified_at=now()
            t.save()
            return JsonResponse({'valid':True,'message':'data saved'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'form_errors':form.errors},content_type='application/json')


@login_required(login_url='/')
def viewOrder(request,id):
    obj=SiteConstants.objects.all()[0]
    data=Oders.objects.all().order_by('-id')
    paginator=Paginator(data,30)
    page_num=request.GET.get('page')
    orders=paginator.get_page(page_num)
    data={
        'title':'View orders',
        'obj':obj,
        'data':request.user,
        'orders':orders,
        'count':paginator.count,
    }
    return render(request,'manager/view_order.html',context=data)


#deleteOrder
@login_required(login_url='/')
@allowed_users(allowed_roles=['admins'])
def deleteOrder(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=Oders.objects.get(orderfields__order_id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':False,'message':'Order deleted successfully.','id':id},content_type='application/json')       
        except Oders.DoesNotExist:
            return JsonResponse({'valid':True,'message':'Order does not exist'},content_type='application/json')

#tabulateOrder
@method_decorator(login_required(login_url='/'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins','secondary']),name='dispatch')
class TabulateOrder(View):
    def get(self,request,id):
        try:
            obj=SiteConstants.objects.all()[0]
            order=OrderFields.objects.get(id__exact=id)
            orders=Oders.objects.get(ordername_id__exact=order.order_id)
            form=OrderFieldsForm()
            customers=OrderFields.objects.all()
            data={
                'title':f'Edit order | {orders.ordername}',
                'obj':obj,
                'data':request.user,
                'editor':orders,
                'form':form,
                'form_id':id,
                'customers':customers
            }
            return render(request,'manager/new_tabulate.html',context=data)
        except User.DoesNotExist:
            return render(request,'manager/404.html',{'title':'Error | Bad Request'},status=400)
    
    def post(self,request,id):
        order=OrderFields.objects.get(id__exact=id)
        form=OrderFieldsForm(request.POST,request.FILES or None,instance=order)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'form_errors':form.errors},content_type='application/json')

@register.filter
def sort_prefix(item):
    print(item)
    

#orderSummary
@login_required(login_url='/')
def orderSummary(request):
    obj=SiteConstants.objects.all()[0]
    now=datetime.datetime.now()
    orders=OrderFields.objects.all().order_by('prefix')
    paginator=Paginator(orders,30)
    page_num=request.GET.get('page')
    orders=paginator.get_page(page_num)
    form=FormUploads()
    data={
        'title':'All orders summary',
        'obj':obj,
        'data':request.user,
        'orders':orders,
        'count':paginator.count,
        'form':form
    }
    return render(request,'manager/order_summary.html',context=data)

#deleteSingleItem
@login_required(login_url='/')
@allowed_users(allowed_roles=['admins','secondary'])
def deleteSingleItem(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=Oders.objects.get(orderfields__id=id)
            obj.delete() 
            return JsonResponse({'valid':False,'message':'Order item deleted successfully.','id':id},content_type='application/json')       
        except Oders.DoesNotExist:
            return JsonResponse({'valid':True,'message':'User does not exist'},content_type='application/json')


#handleUpload
@login_required(login_url='/')
def handleUpload(request,id):
    if request.method == 'POST':
        ob=OrderFields.objects.get(id__exact=id)
        form=FormUploads(request.POST,request.FILES or None,instance=ob)
        if form.is_valid():
            t=form.save(commit=False)
            file_media=request.FILES['media']
            fss=FileSystemStorage()
            filename01=fss.save(file_media.name,file_media)
            file_media_url=fss.url(filename01)
            t.media=file_media
            t.save()
            return JsonResponse({'valid':False,'message':'File saved successfully.'},content_type='application/json')
        else:       
            return JsonResponse({'valid':True,'message':'User does not exist'},content_type='application/json')



#UserUploads
@login_required(login_url='/')
@allowed_users(allowed_roles=['admins'])
def UserUploads(request):
    obj=SiteConstants.objects.all()[0]
    orders=OrderFields.objects.filter(media__isnull=False).all().order_by('-id')
    paginator=Paginator(orders,30)
    page_num=request.GET.get('page')
    orders=paginator.get_page(page_num)
    data={
            'title':'File uploads',
            'obj':obj,
            'data':request.user,
            'count':paginator.count,
            'files':orders,
    }
    return render(request,'manager/uploads.html',context=data)


#UserUploadsDelete
@login_required(login_url='/')
def UserUploadsDelete(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=OrderFields.objects.get(id=id)
            obj.delete() 
            return JsonResponse({'valid':False,'message':'File deleted successfully.','id':id},content_type='application/json')       
        except UserFileUploads.DoesNotExist:
            return JsonResponse({'valid':True,'message':'File does not exist'},content_type='application/json')

