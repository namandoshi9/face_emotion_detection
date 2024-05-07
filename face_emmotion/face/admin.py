from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,EmotionDetection


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['id','username', 'email', 'fullname', 'age', 'gender', 'mobile', 'address']  # Add 'role' to display it in the admin list

admin.site.register(CustomUser, CustomUserAdmin)



@admin.register(EmotionDetection)
class EmotionDetectionAdmin(admin.ModelAdmin):
    list_display = ['id','date', 'happy', 'anger', 'surprise', 'neutral', 'fear', 'sad', 'user_id']

    def user_id(self, obj):
        return obj.user_id

    user_id.short_description = 'User ID'