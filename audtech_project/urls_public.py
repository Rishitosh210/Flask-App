from django.conf.urls import url
from customers import views as Mapping 
from django.conf.urls import url, include
from audtech_analytics import views 
from audtech_analytics import analytics
from audtech_project import views as AP
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings


handler404 = views.handler404
handler500 =views.handler500
urlpatterns = [
    url(r'HomeView/?$',AP.HomeView.as_view()),
    url(r'login/?$', AP.LoginView),
    url(r'logout/$', AP.LogoutView),  
    url(r'^$', Mapping.CreateTenant),
    url(r'processfile/?$', Mapping.ProcessFile),
    url(r'EndProcess/?$', Mapping.EndProcess),
    url(r'AfterProcess/?$', Mapping.AfterProcess),
    url(r'display/$', views.DisplayData),
    url(r'CompanyInfo/$', views.CompanyInformation, name='CompanyInfo'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    #  url(r'signup/$', views.signup, name='signup'),
    #  url(r'login/', views.login, name='login'),
    # url(r'ImageStore/$', views.ImageStore, name='ImageStore'),
    url(r'home/$', views.Home, name='home'),
    url(r'home2/$', views.Home2, name='home2'),
    url(r'PermissionDenied/$', views.PermissionDenied, name='PermissionDenied'),
    url(r'main_page/$', views.main_page, name='main_page'),
    url(r'CreateUser/$', views.CreateUser, name='CreateUser'),
    url(r'Engagement/$',views.EngagementDATA,name='Engagement'),
    # url(r'ERPMap/$',views.ERPMap,name='ERPMap'),
    url(r'navbar/$', views.navbar, name='navbar'),
    url(r'analytics/$', analytics.AnalyticsBoard),
    url(r'total_Tranasacion_according_to_users/(?P<value>[\W.\S+]+)/$', analytics.total_Tranasacion_according_to_users, name='total_Tranasacion_according_to_users'),
    url(r'ManualJE/(?P<value>[\W.\S+]+)/$', analytics.ManualJE, name='ManualJE'),
    url(r'JVAffectingCashAmount/$', analytics.JVAffectingCashAmount, name='JVAffectingCashAmount'),
    url(r'LargeEntry/$', analytics.LargeEntry, name='LargeEntry'),
    # url(r'Jvmonth/(?P<value>[\d.\S+ \d.\S+]+)/$', analytics.Jvmonth, name='Jvmonth'),
    url(r'SameAuthandCreate/$', analytics.SameAuthandCreate, name='Created_and_authorised_by_same_user'),
    url(r'PostedUnposted/(?P<value>[\W.\S+]+)/$', analytics.PostedUnposted, name='PostedUnposted'),
    url(r'Missingvalues/$', analytics.Missingvalues, name='Missingvalues'),
    url(r'LastPeriodEneries/$',analytics.LastPeriodEneries, name='LastPeriodEneries'),
    url(r'JVwithRelatedParties/(?P<value>[\W.\S+]+)/$', analytics.JVwithRelatedParties, name='JVwithRelatedParties'),
    url(r'JVSummary/$', analytics.JVSummary, name='JVSummary'),
    url(r'DuplicatesEntries/$', analytics.DuplicatesEntries, name='DuplicatesEntries'),
    url(r'JVNotBalToZero/$', analytics.JVNotBalToZero, name='JVNotBalToZero'),
    url(r'BackDated/$', analytics.BackDated, name='BackDated'),
    url(r'unusualtimeJE/$', analytics.unusualtimeJE, name='unusualtimeJE'),
    url(r'ShortTextJV/(?P<value>[\W.\S+]+)/$', analytics.ShortTextJV, name='ShortTextJV'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
