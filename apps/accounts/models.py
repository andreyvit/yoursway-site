from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin

from lib.fields import AutoOneToOneField
from accounts.managers import RegistrationManager, ResetManager, EmailManager, ApprovalManager


# Monkey-patching User model
User.add_to_class('site', models.URLField(verify_exists=False, blank=True))
User.add_to_class('email_new', models.EmailField(blank=True))

def _get_name(self):
    return self.first_name
def _set_name(self, name):
    self.first_name = name
User.name = property(_get_name, _set_name)

UserAdmin.fieldsets += (
    ('Byteflow Extensions', {'fields': ('site', 'email_new')}),
    )
UserAdmin.list_display = ('username', 'email', 'first_name', 'is_staff', 'is_active')
UserAdmin.search_fields = ('username', 'first_name', 'email')


ACTION_RECORD_TYPES = (('A', 'Activation'),
                       ('R', 'Password reset'),
                       ('E', 'Email change'),
                       ('C', 'Comment approve')
                       )

class ActionRecord(models.Model):
    """Record that holds activation_key generated upon user registration"""
    user = models.ForeignKey(User)
    action_key = models.CharField(max_length=40)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=1, choices=ACTION_RECORD_TYPES)

    objects = models.Manager()
    registrations = RegistrationManager()
    resets = ResetManager()
    emails = EmailManager()
    approvals = ApprovalManager()

    class Meta:
        db_table = 'actionrecord'

    def __unicode__(self):
        return u"%s record for %s" % (self.get_type_display(), self.user.email)

    @property
    def expired(self):
        """
        Determines whether this Profile's activation key has expired,
        based on the value of the setting ``ACTION_RECORD_DAYS``.

        Set ``ACTION_RECORD_DAYS`` in 0 to disable expiring
        """
        if settings.ACTION_RECORD_DAYS:
            expiration_date = timedelta(days=settings.ACTION_RECORD_DAYS)
            return self.date + expiration_date <= datetime.now()
        else:
            return False


class ActionRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')
    search_fields = ['user']
    list_filter = ('user', 'date')

admin.site.register(ActionRecord, ActionRecordAdmin)
#admin.site.register(Site, SiteAdmin)