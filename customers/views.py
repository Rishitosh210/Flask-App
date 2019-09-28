from customers.forms import TenantForm, GetFile
from django.shortcuts import redirect, render
from django.http import HttpResponse, Http404, JsonResponse
from customers.models import Client
import pandas as pd
import numpy as np
from django.db.models import F
import string
from django.conf import settings
from audtech_analytics.models import Engagement, FinalTable, Mapping
from audtech_analytics.functions import removePunct
from django.core.files.storage import FileSystemStorage
from tenant_schemas.utils import schema_context
from django_pandas.io import read_frame
import os
from django.db.models import Sum, Count
import json
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages


def CreateTenant(request):
    # request.session.modified = True
    context = {}
    if request.method == "GET":
        form = TenantForm()
        context['form'] = form
        return render(request, 'createtenant.html', context)
    elif request.method == "POST":
        form = TenantForm(request.POST)
        context['form'] = form
        if form.is_valid():
            obj = Client(domain_url=(request.POST.get("domain_url") + '.audtech.com'),
                         schema_name=request.POST.get("schema_name"))
            if User.objects.filter(username=request.POST.get("username")).exists():
                context['error'] = "Already Exist"
                return render(request, 'createtenant.html', context)
            else:
                user = User.objects.create_user(username=request.POST.get("username"),
                                                password=request.POST.get("password"))
                obj.user = user
                obj.user_id = user.id
                obj.save()
                context['Good'] = "URL Assigned"
        else:
            messages.error(request, str(form.errors.as_text()))
    return render(request, 'createtenant.html', context)


import datetime
import dateparser
import re


@csrf_protect
def ProcessFile(request):
    # request.session.modified = True
    with schema_context(request.session.get('schema_name')):
        context = {}
        context['logo'] = request.session.get("logo")
        context['client'] = Engagement.objects.filter(user_id=request.session.get('username'))
        context['engagment'] = Engagement.objects.filter(user_id=request.session.get('username'))
        context['username'] = request.session.get('username')
        context['clientname'] = request.session.get('clientname')
        context['engangement'] = request.session.get("engangement")
        if request.method == "GET":
            form1 = GetFile(request)
            context['form'] = form1
            return render(request, 'uploaddata.html', context)
        elif request.method == "POST":
            with schema_context(request.session.get('schema_name')):
                form = GetFile(request, request.POST, request.FILES)
                if form.is_valid():
                    if 'clientname' and 'engangement' not in request.session and request.FILES['inputfile']:
                        context['error'] = "Please check client and engagment"
                        context['form'] = form
                        return render(request, 'uploaddata.html', context)
                    if request.POST.get('client') != "":
                        request.session["clientname"] = request.POST.get('client')
                        request.session['engangement'] = request.POST.get('engagement')

                    myfile = request.FILES['inputfile']
                    fs = FileSystemStorage(location=settings.BASE_DIR + '/filesfolder')  # defaults to   MEDIA_ROOT
                    savedfile = fs.save(myfile.name, myfile)
                    request.session['saved_file'] = savedfile
                    # df=pd.read_csv(settings.BASE_DIR+'/filesfolder/'+str(request.session.get('saved_file')),dtype='unicode')
                    df = pd.read_excel(settings.BASE_DIR + '/filesfolder/' + str(request.session.get('saved_file')))
                    df = df.rename(columns=lambda x: x.strip())
                    lscols = df.columns.tolist()
                    for i in lscols:
                        i = i.strip()
                        try:
                            Mapping.objects.get(source_filed__iexact=i, client=request.session['clientname'],
                                                eng=request.session['engangement'])
                        except Mapping.DoesNotExist:
                            return redirect('/AfterProcess')
                    Fo = Mapping.objects.filter(eng=request.session.get("engangement"))
                    context['Fo'] = Fo
                    dicto = {}
                    for idx in range(len(df.index)):
                        for i in lscols:
                            i = i.strip()
                            f = Mapping.objects.get(source_filed__iexact=i, client=request.session['clientname'],
                                                    eng=request.session['engangement'])
                            arg2 = df[i][idx]
                            arg2 = removePunct(arg2)
                            dicto[f.final_field] = arg2
                            dicto['client'] = request.session.get('clientname')
                            dicto['engangement'] = request.session.get('engangement')
                        FinalTable.objects.bulk_create([FinalTable(**dicto)])
                        FinalTable.objects.filter(CreatedBy='0', StatusPostedUnposted='0', AuthorisedBy='0') \
                            .update(CreatedBy='None', AuthorisedBy='None', StatusPostedUnposted='None')
                        df = df.head(20)
                    context['frame'] = df.to_html(index=False)
                    os.remove(settings.BASE_DIR + '/filesfolder/' + str(request.session.get('saved_file')))
                    return render(request, 'process.html', context)
                else:
                    context['form'] = form
                    return render(request, 'process.html', context)


@csrf_protect
def AfterProcess(request):
    context = {}
    context['logo'] = request.session.get("logo")
    if request.method == 'GET':
        with schema_context(request.session.get('schema_name')):
            # df=pd.read_csv(settings.BASE_DIR+'/filesfolder/'+str(request.session['saved_file']),dtype='unicode')
            df = pd.read_excel(settings.BASE_DIR + '/filesfolder/' + str(request.session.get('saved_file')))
            df = df.head(10)
            context['username'] = request.session.get('username')
            context['frame'] = df.to_html(index=False, classes='')
            context['engangement'] = request.session.get("engangement")
            context['clientname'] = request.session.get("clientname")
            context['erp'] = request.session.get('erp')
            count = pd.DataFrame(df.columns)
            context['count'] = count.values.tolist()
            return render(request, 'buttons.html', context)
    if request.method == 'POST':
        with schema_context(request.session.get('schema_name')):
            print(request.session.get("schema_name"))
            # df=pd.read_csv(settings.BASE_DIR+'/filesfolder/'+str(request.session['saved_file']),dtype='unicode')
            df = pd.read_excel(settings.BASE_DIR + '/filesfolder/' + str(request.session.get('saved_file')))
            df = df.rename(columns=lambda x: x.strip())
            count = pd.DataFrame(df.columns)
            context['count'] = count.values.tolist()
            for i, j in zip(range(len(df.columns)), range(1, len(df.columns) + 1)):
                Mapping.objects.create(source_filed=df.columns[i],
                                       final_field=(request.POST.get('C' + str(j))).replace(' ', ''),
                                       column_no=df.columns[i], client=request.session['clientname'],
                                       eng=request.session['engangement'])
            lscols = df.columns.tolist()
            for i in lscols:
                try:
                    Mapping.objects.get(source_filed__iexact=i, eng=request.session.get("engangement"))
                    return redirect('/EndProcess')
                except Mapping.DoesNotExist:
                    return HttpResponse(str(i))
            return render(request, 'buttons.html', context)
        return render(request, 'buttons.html', context)


@csrf_protect
def EndProcess(request):
    context = {}
    context['logo'] = request.session.get("logo")
    context['username'] = request.session.get('username')
    context['engangement'] = request.session.get("engangement")
    context['clientname'] = request.session.get("clientname")
    with schema_context(request.session.get('schema_name')):
        Fo = Mapping.objects.filter(eng=request.session.get("engangement"))
        context['Fo'] = Fo
        df = pd.read_excel(settings.BASE_DIR + '/filesfolder/' + str(request.session.get('saved_file')))
        # df=pd.read_csv(settings.BASE_DIR+'/filesfolder/'+ str(request.session.get('saved_file')))
        df = df.fillna('0')
        df = df.rename(columns=lambda x: x.strip())
        lscols = df.columns.tolist()
        dicto = {}
        for idx in range(len(df.index)):
            for i in lscols:
                i = i.strip()
                f = Mapping.objects.get(source_filed__iexact=i, client=request.session['clientname'],
                                        eng=request.session['engangement'])
                arg2 = df[i][idx]
                arg2 = removePunct(arg2)
                dicto[f.final_field] = arg2
                dicto['client'] = request.session.get('clientname')
                dicto['engangement'] = request.session.get('engangement')
            FinalTable.objects.bulk_create([FinalTable(**dicto)])
            FinalTable.objects.filter(CreatedBy='0', StatusPostedUnposted='0', AuthorisedBy='0') \
                .update(CreatedBy='None', AuthorisedBy='None', StatusPostedUnposted='None')
        df = df.head(20)
        context['frame'] = df.to_html(index=False)
        os.remove(settings.BASE_DIR + '/filesfolder/' + str(request.session.get('saved_file')))
        return render(request, 'process.html', context)
    return render(request, 'process.html', context)


def UpdateMapping(request):
    context = {}
    if request.method == 'GET':
        form = match()
        df = pd.read_csv(settings.BASE_DIR + '/filesfolder/' + str(request.session['saved_file']), dtype='unicode')
        df = df.head(5)
        context['username'] = request.session.get('username')
        context['frame'] = df.to_html(index=False, classes='')
        context['eng'] = request.session.get("engangement")
        context['clientname'] = request.session.get("clientname")
        context['erp'] = request.session.get('erp')
        count = pd.DataFrame(df.columns)
        context['count'] = count.values.tolist()
        context['form'] = form
        return render(request, 'UpdateMapping.html', context)
    if request.method == 'POST':
        with schema_context(request.session.get('schema_name')):
            df = pd.read_csv(settings.BASE_DIR + '/filesfolder/' + str(request.session['saved_file']), dtype='unicode')
            count = pd.DataFrame(df.columns)
            context['count'] = count.values.tolist()
            for i, j in zip(range(len(df.columns)), range(1, len(df.columns) + 1)):
                Mapping.objects.update(source_filed=df.columns[i], final_field=request.POST.get('C' + str(j)),
                                       column_no=df.columns[i]).filter(eng=request.session.get('engangement'))
            lscols = df.columns.tolist()
            columnnames = [i for i in lscols]
            for i in columnnames:
                try:
                    Mapping.objects.get(source_filed__iexact=i, eng=request.session.get('engangement'))
                    return redirect('/EndProcess')
                except Mapping.DoesNotExist:
                    return HttpResponse(str(i))
    return render(request, 'UpdateMapping.html', context)
