from django import forms
from customers.models import Client
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission, Group
from audtech_analytics.models import Engagement, CompanyInfo, FinalTable
# from customers.models import Mapping
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import AppendedText
from audtech_analytics.constants import Country_list
from crispy_forms.layout import Layout, Submit, Row, Column
from audtech_project import settings
from django.core.files.storage import FileSystemStorage
from tenant_schemas.utils import schema_context


# add login required to required views

class TenantForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(TenantForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['username'] = forms.CharField(max_length=80, label='User Name')
        self.fields['schema_name'] = forms.CharField(max_length=80, label='Schema Name')
        self.fields['domain_url'] = forms.CharField(max_length=80, label='Domain Url')
        self.fields['password'] = forms.CharField(max_length=80, widget=forms.PasswordInput, label='Password')
        self.helper.add_input(Submit('submit', 'Signup', css_class='btn-primary', css_id='submit'))
        self.helper.form_method = 'POST'


class companyinfo(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = '__all__'
        exclude = ('user_id',)


class GetFile(forms.Form):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        kwargs.setdefault('label_suffix', '')
        super(GetFile, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        uq = Engagement.objects.values_list('name', flat=True).filter(
            user_id=self.request.session['username']).distinct()
        yq = Engagement.objects.values_list('engagement_name', flat=True) \
            .filter(user_id=self.request.session['username']).distinct()
        last = []
        last.append(("", ""))
        for i in uq:
            last.append((i, i))
        eng = []
        eng.append(("", ""))
        for i in yq:
            eng.append((i, i))
        self.fields['client'] = forms.ChoiceField(choices=last, required=False)
        self.fields['engagement'] = forms.ChoiceField(choices=eng, required=False)
        self.fields['inputfile'] = forms.FileField(label='Select File')
        self.helper.form_id = "form_Cli_eng"
        self.helper.add_input(Submit('submit', 'Process', css_class='btn btn-primary ', css_id='submit_it'))
        self.helper.form_method = 'POST'


# class match(forms.Form):
#     # User_field=forms.CharField( max_length=60, required=False)
#     class Meta:
#         model = Mapping
#         exclude = ('final_field',)

#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault('label_suffix', '')
#         super(match, self).__init__(*args, **kwargs)
#         uq=Mapping.objects.values_list('final_field',flat=True).distinct()
#         last=[]
#         for i in uq:
#             last.append((i,i))
#         self.helper = FormHelper()
#         self.form_class='shounak'
#         self.fields['final_field']=forms.ChoiceField( choices=last,label="Audtech Field")
#         # self.fields['1']=forms.ChoiceField( choices=last,label="Audtech Field")
#         # self.fields['done'] = forms.BooleanField(required=False,label="Click if the mapping is done")
#         self.helper.add_input(Submit('submit', 'Save', css_class='btn-primary'))
#         self.helper.form_method = 'POST'

from django.contrib.auth.forms import UserCreationForm


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'user_permissions', 'last_name', 'email', 'password1', 'password2')
        # exclude = ('user_permissions',)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        uq = Permission.objects.values_list('name', flat=True) \
            .filter(codename__in=['is_read', 'is_import', 'is_analytics', 'is_report', 'add_engagement'])
        last = []
        for i in uq:
            last.append((i, i))
        self.fields['username'] = forms.CharField(max_length=20, required=False)
        # self.fields['groups'].label='Roles'
        self.fields['user_permissions'] = forms.MultipleChoiceField(choices=last, widget=forms.CheckboxSelectMultiple(),
                                                                    required=False)
        self.helper.add_input(Submit('submit', 'Create User', css_class='button'))
        self.helper.form_class = 'form-control'
        self.helper.form_method = 'POST'


class EngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement
        exclude = ('user_id', 'financial_management_system', 'peroid_frequency', 'additional_info')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EngagementForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'Shounak'
        self.fields['name'] = forms.CharField(label='Entity Name', max_length=20, required=True)
        self.fields['fiscal_start_month'] = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS,
                                                            widget=forms.DateInput, required=False)
        self.fields['fiscal_end_month'] = forms.DateField(widget=forms.DateInput, required=False)
        self.fields['company_type'] = forms.CharField(label='Entity Type', max_length=20, required=True)
        self.helper.add_input(Submit('submit', 'Create Enagagements', css_class='btn-primary'))
        self.helper.form_method = 'POST'


class FinalTableFilter(forms.ModelForm):
    class Meta:
        model = FinalTable
        fields = ['MainAccountCode', 'MainAccountName', 'AccountCategory', 'JournalDate']

    def __init__(self, request, *args, **kwargs):
        self.request = request
        # self.request = kwargs.pop("request")
        kwargs.setdefault('label_suffix', '')
        super(FinalTableFilter, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        print(self.request.session.get('clientname'))
        with schema_context(request.session.get('schema_name')):
            try:
                uq = FinalTable.objects.filter(client=self.request.session['clientname'],
                                               engangement=self.request.session['engangement']) \
                    .values_list('AccountCategory', flat=True).distinct()
                last = []
                last.append(("", ""))
                for i in uq:
                    last.append((i, i))
                self.fields['AccountCategory'] = forms.ChoiceField(choices=last, label='Account Category',
                                                                   required=False)
                uq = FinalTable.objects.filter(client=self.request.session['clientname'],
                                               engangement=self.request.session['engangement']) \
                    .values_list('MainAccountCode', flat=True).distinct()
                last1 = []
                last1.append(("", ""))
                for i in uq:
                    last1.append((i, i))
                self.fields['MainAccountCode'] = forms.ChoiceField(choices=last1, label='Main Account Code',
                                                                   required=False)
                uq = FinalTable.objects.filter(client=self.request.session['clientname'],
                                               engangement=self.request.session['engangement']) \
                    .values_list('JournalDate', flat=True).distinct()
                last2 = []
                last2.append(("", ""))
                for i in uq:
                    last2.append((i, i))
                self.fields['JournalDate'] = forms.ChoiceField(choices=last2, label='Journal Date', required=False)
                uq = FinalTable.objects.filter(client=self.request.session['clientname'],
                                               engangement=self.request.session['engangement']) \
                    .values_list('MainAccountName', flat=True).distinct()
                last3 = []
                last3.append(("", ""))
                for i in uq:
                    last3.append((i, i))
                self.fields['MainAccountName'] = forms.ChoiceField(choices=last3, label='Main Account Name',
                                                                   required=False)
            except:
                pass
            self.helper.form_method = 'POST'

# class PermissinoForm(forms.ModelForm):

#     class Meta:
#         model = Permission
#         fields= '__all__'
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault('label_suffix', '')
#         super(PermissinoForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.add_input(Submit('submit', 'Click for', css_class='btn-primary'))
#         self.helper.form_method = 'POST'
