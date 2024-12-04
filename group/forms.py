from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"
        widgets = {
            "permissions": FilteredSelectMultiple('Permission', is_stacked=False)
        }

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css',)
        }
        js = ('/admin/jsi18n/',)


    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields["permissions"].queryset = Permission.objects.all().exclude(content_type__app_label__in=["admin", "auth", "sequences", "sessions", "contenttypes", "main", "account","group"])
        self.fields["permissions"].label_from_instance = lambda obj: "%s"% obj.name
