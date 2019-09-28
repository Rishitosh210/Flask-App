from django.shortcuts import render,redirect
from audtech_analytics.models import FinalTable
from customers.forms import FinalTableFilter
from django.http import HttpResponse
from audtech_analytics.models import Engagement
import pandas as pd
import numpy as np
from django.contrib.auth.decorators import login_required
from django_pandas.io import read_frame
from django.contrib.auth.decorators import permission_required
from django.db.models.functions import Cast
from django.db.models import Count,Case, CharField, Value, When,Max,Q,F,Sum,FloatField
from tenant_schemas.utils import schema_context
from audtech_analytics.functions import missing_values
from django.contrib import messages
from django.db.models.functions import Length
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
from django.db.models.functions import Extract,TruncMonth,ExtractMonth,ExtractWeekDay
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import datetime
# @permission_required('audtech_analytics.is_analytics',login_url='/PermissionDenied')
def AnalyticsBoard(request):
	filename =request.session.get('saved_file')
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	context['filename']=filename
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']= request.session.get('schema_name')
	context['engangement']=engangement
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	with schema_context(request.session.get('schema_name')):
		FilterClientEng=FinalTable.Filter(clientname,engangement)
		# ===========================================================================
						# charts
		context['dataset']=FilterClientEng\
		.values("StatusPostedUnposted")\
		.annotate(survived_count=Count('StatusPostedUnposted'),not_survived_count=Count('JournalType'))\
		# ====================================================================
						#''' Missing Values '''
		obj=FilterClientEng.order_by('SrNo')
		context['transaction']=obj.count()
		# print('========'+str(engangement))
		qs=read_frame(obj)
		df=pd.DataFrame(qs).drop(['client','engangement','user_id','Upload_Date','id'], axis=1)
		# =============================================================================
		df['SrNo']=df['SrNo'].astype(float)
		dcf=pd.DataFrame(missing_values(df['SrNo']))
		dcf=dcf.count()
		context['missing']=dcf.to_csv(index=False)
		# ==============================================================================
			# ''' Top users number of entries / value '''
		JE=FilterClientEng\
			.values('CreatedBy')\
			.annotate(JE=Count('CreatedBy'))\
			.annotate(Credit=Cast('CreditAmount', FloatField()),Debit=Cast('DebitAmount', FloatField()))\
			.annotate(Credit=Sum('Credit'),Debit=Sum('Debit'))
		context['JEuser']=JE
		# ==================================================================================
		# ''' Bottom users number of entries / value '''
		JE=FilterClientEng\
			.values('CreatedBy')\
			.annotate(JE=Count('CreatedBy'))\
			.annotate(Credit=Cast('CreditAmount', FloatField()),Debit=Cast('DebitAmount', FloatField()))\
			.annotate(Credit=Sum('Credit'),Debit=Sum('Debit'))\
			.order_by('-JE')
		context['JEuser']=JE
		# ==================================================================================
		# ''' Posted / Un posted - Authorised / Un Authorised JE '''
		posted_unposted=FilterClientEng\
		.values('StatusPostedUnposted')\
		.annotate(Credit=Cast('CreditAmount', FloatField()),Debit=Cast('DebitAmount', FloatField()))\
		.annotate(posted_unposted=Count('StatusPostedUnposted'),Credit=Sum('Credit'),Debit=Sum('Debit'))
		context['pos_unpos']=posted_unposted
		# =======================================================================================
		# '''Manual JE / System generated JE in terms of number and value  '''
		Je_auto_manual=FilterClientEng\
		.values('TransactionType')\
		.annotate(Generated=Count('TransactionType'))
		context['TransactionType']=Je_auto_manual
		# ==========================================================================
			#'''created and authorized by same user'''
		data1=FilterClientEng\
		.filter(AuthorisedBy__iregex=F('CreatedBy'))
		context['cre_equ_auth_count']=data1.count()
	# =====================================================================================
			# JV passby Month
		Jv_month=FilterClientEng\
		.annotate(Mahina=ExtractMonth("JournalDate"))\
		.values('Mahina')\
		.annotate(month=Count("Mahina"))\
		.annotate(Credit=Cast('CreditAmount', FloatField()),Debit=Cast('DebitAmount', FloatField()))\
		.annotate(Credit=Sum('Credit'),Debit=Sum('Debit'))\
		.order_by('Mahina')
		context['Jvmonth']=Jv_month
		# =================================================
			#JV's with related parties
		#     JvParties=FinalTable.objects\
		#     .values('MainAccountName')\
		#     .annotate(c=Count('MainAccountName'))\
		#     .filter(client=clientname,engangement=engangement)
		#     context['JvP']=JvParties
	# =======================================================================================
		#JV's On Weekend
		Jvholidays=FilterClientEng\
		.annotate(Week=ExtractWeekDay("JournalDate"))\
		.values('Week')\
		.annotate(week=Count("Week"))\
		.filter(JournalDate__week_day__in=[1,7])\
		.annotate(Credit=Cast('CreditAmount', FloatField()),Debit=Cast('DebitAmount', FloatField()))\
		.annotate(Credit=Sum('Credit'),Debit=Sum('Debit'))\
		.order_by("Week")
		context['JVweekend']=Jvholidays
	#=================================================================================================
		#JV's with Little Description
		# JvLittleDesc=FilterClientEng\
		# .values('ShortText','CreatedBy')\
		# .annotate(len=Length('ShortText'))\
		# .filter(len__lte=25)
		# context['JvLittleDesc']=JvLittleDesc
	#========================================================================================\
		# Debit-Credit Amount
		JVCreDebAmount=FilterClientEng\
		.values('CreditAmount','DebitAmount' )\
		.annotate(Credit=Cast('CreditAmount', FloatField()),Debit=Cast('DebitAmount', FloatField()))\
		.aggregate(Sum('Credit'),Sum('Debit'))
		context['DebCre']=JVCreDebAmount
	# #==========================================-------------------------------
		return render(request,'analytics.html',context)
# @permission_required('audtech_analytics.is_report',login_url='/PermissionDenied')
				# .values('MainAccountCode','MainAccountName','JournalDate','SubAccountCode','SubAccountName','AccountCategory','DebitAmount','CreditAmount')
#================================================================================================================
def ShortTextJV(request,value):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
			ShortTextJV=FinalTable.objects\
			.filter(client=clientname,engangement=engangement,ShortText=value)
			context['ShortTextJV']=ShortTextJV
			return render(request,'Analytics/ShortTextJV.html',context)
	return render(request,'Analytics/ShortTextJV.html',context)
def DuplicatesEntries(request):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		if request.method =="POST":
			for i in request.POST.getlist("filter"):
				JETest=FinalTable.objects\
				.filter(client=clientname,engangement=engangement)\
				.annotate(name_count=Count(i)).filter(name_count__gt=1)
				context['JVDuplicate']=JETest
				print(i)
				return render(request,'Analytics/DuplicateEntries.html',context)
		return render(request,'Analytics/DuplicateEntries.html',context)
	#========================================================================================================================
def JVSummary(request):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
			context['Currency']=request.session['Currency']
	except:
			pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		if request.method == "GET":
			form = FinalTableFilter(request)
			context['form']=form
			return render(request,'Analytics/JVSummary.html',context)
		if request.method =="POST":
			form = FinalTableFilter(request,request.POST)
			if request.POST.get('JournalDate') == "":
				context['form']=form
				context['messages']="Please select valid date"
				return render(request,'Analytics/JVSummary.html',context)
			else:
				JE=FinalTable.objects\
				.filter(Q(client=clientname,engangement=engangement)\
				& Q(JournalDate=request.POST.get('JournalDate'))
				& Q(MainAccountCode__contains=request.POST.get('MainAccountCode')) \
				& Q(MainAccountName__contains=request.POST.get('MainAccountName'))\
				& Q(AccountCategory__contains=request.POST.get('AccountCategory')))\
				.values('MainAccountCode','MainAccountName','JournalDate','SubAccountCode','SubAccountName','AccountCategory','DebitAmount','CreditAmount')
				if not JE:
					context['NoRecords']= "No records found for selected fields"
				context['JEuser']=JE
				context['form']=form
				return render(request,'Analytics/JVSummary.html',context)
		return render(request,'Analytics/JVSummary.html',context)
	return render(request,'Analytics/JVSummary.html',context)
# @permission_required('audtech_analytics.is_report',login_url='/PermissionDenied')
def JVAffectingCashAmount(request):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		Jv_Cash=FinalTable.objects\
		.filter(client=clientname,engangement=engangement,MainAccountName__contains="CASH")\
		.values("SrNo","JournalDate","JournalNumber","DebitAmount","CreditAmount","MainAccountName")
		context['Jv_Cash']=Jv_Cash
		return render(request,'Analytics/JVAffectingCashAmount.html',context)
def ManualJE(request,value):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		Je_auto_manual=FinalTable.objects\
		.filter(client=clientname,engangement=engangement,TransactionType=value)
		context['Je_auto_manual']=Je_auto_manual
		for I in Je_auto_manual:
			context['I']=I
		return render(request,'Analytics/ManualJE.html',context)

# @permission_required('audtech_analytics.is_report',login_url='/PermissionDenied')
def total_Tranasacion_according_to_users(request,value):
	filename =request.session.get('saved_file')
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		JE=FinalTable.objects\
		.filter(client=clientname,CreatedBy=value,engangement=engangement)
		context['JEuser']=JE
		for I in JE:
			context['I']=I
		return render(request,'Analytics/total_Tranasacion_according_to_users.html',context)

# @permission_required('audtech_analytics.is_report',login_url='/PermissionDenied')
def SameAuthandCreate(request):
	filename =request.session.get('saved_file')
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		data1=FinalTable.objects\
		.filter(client=clientname,engangement=engangement)\
		.filter(AuthorisedBy__iregex=F('CreatedBy'))
		context['cre_equ_auth']=data1
		return render(request,'Analytics/SameAuthandCreate.html',context)

from django.db.models import Q
# @permission_required('audtech_analytics.is_report',login_url='/PermissionDenied')
def PostedUnposted(request,value):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		posted_unposted=FinalTable.objects\
		.filter(Q(client=clientname)&Q(engangement=engangement)).order_by('SrNo')\
		.filter(StatusPostedUnposted=value)
		context['pos_unpos']=posted_unposted
		for I in posted_unposted:
			context['I']=I
		return render(request,'Analytics/PostedUnposted.html',context)
		# return render(request,'Analytics/PostedUnposted.html',context)
	return render(request,'Analytics/PostedUnposted.html',context)

# @permission_required('audtech_analytics.is_report',login_url='/PermissionDenied')
def Missingvalues(request):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	context['logo']=request.session.get("logo")
	with schema_context(request.session.get('schema_name')):
		obj=FinalTable.Filter(clientname,engangement).order_by('SrNo')
		qs=read_frame(obj)
		df=pd.DataFrame(qs).drop(['client','engangement','user_id','Upload_Date','id'], axis=1)
		df['SrNo']=df['SrNo'].astype(float)
		dcf=pd.DataFrame(missing_values(df['SrNo'])).rename(columns={0:'Missing Values'})
		context['missing']=dcf.to_html()
		return render(request,'Analytics/Missingvalues.html',context)
# @permission_required('audtech_analytics.is_report',login_url='/PermissionDenied')
def JVwithRelatedParties(request,value):
	filename =request.session.get('saved_file')
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		JvParties=FinalTable.objects\
		.filter(client=clientname,engangement=engangement,MainAccountName=value)
		context['JvP']=JvParties
		for JE in JvParties:
			context['JE']=JE
		return render(request,'Analytics/JVwithRelatedParties.html',context)


def LargeEntry(request):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		LargeEnteries=FinalTable.objects\
		.filter(client=clientname,engangement=engangement)\
		.order_by('-CreditAmount')[:10]
		context['LargeEnteries']=LargeEnteries
		# for I in LargeEnteries:
		#         context['I']=I
		return render(request,'Analytics/LargeEnteries.html',context)

from datetime import timedelta
def LastPeriodEneries(request):
	context={}
	context['logo']=request.session.get("logo")
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']= clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		try:
			eng=Engagement.objects.get(name=clientname,engagement_name=engangement)
			# I=datetime.datetime.strftime(eng.fiscal_end_month,'%Y-%m-%d %H:%M:%S')
			# I=datetime.datetime.strptime(I,'%Y-%m-%d %H:%M:%S')
			lastdate= eng.fiscal_end_month - timedelta(days=5)
			LastPeriodEneries=FinalTable.Filter(clientname,engangement).filter(JournalDate__range=[lastdate,eng.fiscal_end_month])
			context['LastPeriodEneries']=LastPeriodEneries
			return render(request,'Analytics/LastPeriodEneries.html',context)
		except:
			return render(request,'Analytics/LastPeriodEneries.html',context)
		return render(request,'Analytics/LastPeriodEneries.html',context)
#==========================================================================================

def JVNotBalToZero(request):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		JVBal_Zero=FinalTable.Filter(clientname,engangement)
		# paginator = Paginator(JVBal_Zero, 5) 
		# page = request.GET.get('page')
		# JVBalZero = paginator.get_page(page)
		s=[]
		for I in JVBal_Zero:
			# context['I']=I
			if I.Notbalance :
				s.append(I.Notbalance)
			context['Jv0']=JVBal_Zero.filter(CreditAmountFC__in=s)
		return render(request,'Analytics/JVNotBalToZero.html',context)
	return render(request,'Analytics/JVNotBalToZero.html',context)
#===========================================================================================
def BackDated(request):
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context={}
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		obj=FinalTable.Filter(clientname,engangement)
		for i in obj:
			print(i.date_gaps)
			if i.date_gaps:
				Backdated=obj.filter(JournalDate=i.JournalDate,PostingDate=i.PostingDate)
				context['Backdated']=Backdated
				for I in Backdated:
					context['I']=I
				return render(request,'Analytics/backdated.html',context)
		return render(request,'Analytics/backdated.html',context)
	return render(request,'Analytics/backdated.html',context)

#============================================================================================
def unusualtimeJE(request):
	context={}
	clientname =request.session.get('clientname')
	engangement =request.session.get('engangement')
	context['logo']=request.session.get("logo")
	try:
		context['Currency']=request.session['Currency']
	except:
		pass
	context['clientname']=clientname
	context['username']=request.session.get('username')
	context['customer']=request.session.get('schema_name')
	context['engangement']=engangement
	with schema_context(request.session.get('schema_name')):
		time=FinalTable.Filter(clientname,engangement)
		s=[]
		for i in time:
			context['I']=i
			if i.ubuntu:
				s.append(i.ubuntu)
		context['unusualtimeJE']=time.filter(JournalDate__in=s)
		return render(request,'Analytics/unusualtimeJE.html',context)
	return render(request,'Analytics/unusualtimeJE.html',context)