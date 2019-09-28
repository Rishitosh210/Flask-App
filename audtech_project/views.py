from customers.models import Client
from django.conf import settings
from django.db import utils
from django.views.generic import TemplateView
from django.shortcuts import render,redirect
from tenant_schemas.utils import remove_www
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
from tenant_schemas.utils import schema_context
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages 
from audtech_analytics.models import CompanyInfo
from django.contrib.sessions.models import Session
def LoginView(request):
    context={}
    if request.method=='GET':
        return render(request,'login1.html',context)
    elif request.method=='POST':
        username=str(request.POST.get("login"))
        password=str(request.POST.get("password"))
        if request.POST.get("company"):
            with schema_context(request.POST.get("company")):
                result=authenticate(username=username,password=password)
                if result:
                    login(request,result)
                    CL=CompanyInfo.objects.get(name=request.POST.get("company"))
                    uploaded_file_url = CL.logo.url
                    request.session['logo']=uploaded_file_url
                    print(request.session.get('logo'))
                    request.session['username']=username
                    request.session['schema_name']=request.POST.get("company")
                    print('=====SCHEMA IS==============='+str(request.session.get('schema_name')+"for user+"+str(request.session.get("username"))))
                    return redirect('/home')
                else:
                    context['error']="Login Failed"
        else:   
            result=authenticate(username=username,password=password)
            if result:
                if username=="Audtech":
                    login(request,result)
                    return redirect('/')
                else:
                    login(request,result)
                    client=Client.objects.get(user_id=request.user.id)
                    request.session['username']=username
                    request.session['schema_name']=client.schema_name
                    print("schema is " + request.session.get("schema_name"))
                    with schema_context(str(client.schema_name)):
                        if CompanyInfo.objects.filter(user_id=username).exists():
                            return redirect('/home2')
                        else:
                            return redirect('/CompanyInfo')
            else:
                context['error']="Login Failed"
    return render(request,'login1.html',context)


def LogoutView(request):
    logout(request)
    # Session.objects.all().delete()
    # messages.error(request, 'Logout Success'+str(request.session.get("username")))
    return redirect('/login')
    
class HomeView(TemplateView):
    template_name = "index_public.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        hostname_without_port = remove_www(self.request.get_host().split(':')[0])

        try:
            Client.objects.get(schema_name='public')
        except utils.DatabaseError:
            context['need_sync'] = True
            context['shared_apps'] = settings.SHARED_APPS
            context['tenants_list'] = []
            return context
        except Client.DoesNotExist:
            context['no_public_tenant'] = True
            context['hostname'] = hostname_without_port

        if Client.objects.count() == 1:
            context['only_public_tenant'] = True

        context['tenants_list'] = Client.objects.all()
        return context
