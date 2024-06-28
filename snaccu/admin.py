from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from snaccu.models import Friend, User

admin.site.site_header = 'Accknox Administration'
# admin.site.site_title = 'LakshmiShree Site Admin'
admin.site.index_title  =  "Users Admin"


class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["id", "email", "first_name", "last_name", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ("User Credential", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name",]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "last_name", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
admin.site.register(Friend)