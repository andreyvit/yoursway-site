from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from accounts.models import ActionRecord

class ProfileForm(forms.Form):
    """Form for editing user profile"""
    name = forms.CharField(max_length=30, required=False, label=_(u'Name'))
    email = forms.EmailField(max_length=128, required=False, label=_(u'Email'), help_text=_(u"Changing email requires activation"))
    site = forms.CharField(max_length=200, required=False, label=_(u'Site'))
    password1 = forms.CharField(widget=forms.PasswordInput(), required=False, label=_(u'Password'), help_text=_(u"Leave blank to keep current"))
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False, label=_(u'Password'), help_text=_(u"Repeat, to catch typos"))

    def __init__(self, user, *args, **kwargs):
        """Setting initial values"""
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['name'].initial = self.user.first_name
        self.fields['email'].initial = self.user.email
        self.fields['site'].initial = self.user.site

    def clean_email(self):
        """Validates that no user have same email"""
        if self.cleaned_data['email'] and (self.cleaned_data['email'] != self.user.email):
            try:
                User.objects.get(email__iexact=self.cleaned_data['email'])
            except User.DoesNotExist:
                return self.cleaned_data['email']
            raise forms.ValidationError(_(u'This address already belongs to other user'))
        elif not self.cleaned_data['email'] and not self.user.userassociation_set.count():
            raise forms.ValidationError(_(u'This field is required'))
        else:
            return self.cleaned_data['email']

    def clean_password2(self):
        """Validates that the two password inputs match."""
        if self.cleaned_data['password1'] == self.cleaned_data['password2']:
            return self.cleaned_data['password2']
        else:
            raise forms.ValidationError(_(u'You must type the same password each time'))

    def clean_site(self):
        if self.cleaned_data['site'] and self.cleaned_data['site'][:7] != 'http://':
            return 'http://%s' % self.cleaned_data['site']
        else:
            return self.cleaned_data['site']

    def save(self):
        """Saves user profile"""
        self.user.first_name = self.cleaned_data['name']
        self.user.site = self.cleaned_data['site']
        if self.cleaned_data['email'] != self.user.email:
            ActionRecord.emails.create_email_change(self.user, self.cleaned_data['email'])
        # set password only if changed
        if self.cleaned_data.get('password1'):
            self.user.set_password(self.cleaned_data['password1'])
        self.user.save()


class OpenidForm(forms.Form):
    openid_url = forms.URLField(label='OpenID', max_length=200, required=True)

    def __init__(self, session, *args, **kwargs):
        super(OpenidForm, self).__init__(*args, **kwargs)
        self.session = session

    def get_site_url(self):
        from django.contrib.sites.models import Site
        site = Site.objects.get_current()
        return '://'.join(['http', site.domain])

    def clean_openid_url(self):
        #FIXME: lib.auth is not found
        from lib.auth import get_consumer
        from yadis.discover import DiscoveryFailure
        from urljr.fetchers import HTTPFetchingError
        consumer = get_consumer(self.session)
        errors = []
        try:
            self.request = consumer.begin(self.cleaned_data['openid_url'])
        except HTTPFetchingError, e:
            errors.append(str(e.why))
        except DiscoveryFailure, e:
            errors.append(str(e[0]))
        if hasattr(self, 'request') and self.request is None:
            errors.append('OpenID service is not found')
        if errors:
            raise forms.ValidationError(errors)

    def auth_redirect(self, target, view_name, *args, **kwargs):
        from django.core.urlresolvers import reverse
        site_url = self.get_site_url()
        trust_url = settings.OPENID_TRUST_URL or (site_url + '/')
        return_to = site_url + reverse(view_name, args=args, kwargs=kwargs)
        self.request.return_to_args['redirect'] = target
        return self.request.redirectURL(trust_url, return_to)
