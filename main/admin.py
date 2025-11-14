from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Pitch, PitchType, Booking


class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username', 
        'email', 
        'full_name', 
        'phone_number', 
        'role', 
        'is_staff', 
        'is_active'
    )
    search_fields = ('username', 'email', 'full_name', 'phone_number')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('full_name', 'email', 'phone_number')}),
        ('Quyền hạn & Vai trò', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Ngày giờ', {'fields': ('last_login', 'created_at')}),
    )

class PitchAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'pitch_type', 
        'address', 
        'base_price_per_hour', 
        'is_available', 
        'created_at'
    )
    search_fields = ('name', 'address')
    ordering = ('name',)
    raw_id_fields = ('pitch_type',)

class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'pitch', 
        'user', 
        'booking_date', 
        'start_time', 
        'duration_hours',
        'final_price', 
        'status'
    )
    search_fields = ('pitch__name', 'user__username', 'user__full_name')
    date_hierarchy = 'booking_date'
    readonly_fields = ('created_at', 'duration_hours', 'final_price')
    raw_id_fields = ('user', 'pitch')

class PitchTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass 
    
admin.site.register(User, CustomUserAdmin)
admin.site.register(PitchType, PitchTypeAdmin)
admin.site.register(Pitch, PitchAdmin)
admin.site.register(Booking, BookingAdmin)