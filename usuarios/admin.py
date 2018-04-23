from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import User, TipoUsuario

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
            (('LEONUX'), {'fields': ('tipo_usuario',)}),
    )
admin.site.register(User, MyUserAdmin)

@admin.register(TipoUsuario)
class TipoUsuarioAdmin(admin.ModelAdmin):
    pass
