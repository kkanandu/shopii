from django.contrib import admin
from .models import *
from django.utils.timezone import now


admin.site.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'submitted_at', 'admin_reply', 'replied_at')
    list_filter = ('submitted_at',)
    search_fields = ('user__username', 'message', 'subject')
    readonly_fields = ('submitted_at')

    def has_add_permission(self, request):
        return False
    def is_replied(self, obj):
        return bool(obj.admin_reply)
    is_replied.boolean = True
    is_replied.short_description = "Replied"


    def save_model(self, request, obj, form, change):
        if obj.admin_reply and not obj.replied_at:
            obj.replied_at = now()
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Exclude 'replied_at' from the admin form
        return [f for f in fields if f != 'replied_at']

admin.site.register(Notification)

admin.site.register(ChatMessage)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    readonly_fields = ('sender', 'timestamp')

    def has_add_permission(self, request, obj):
        # Allow adding new messages only if ChatSession exists
        return obj is not None

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "created_at")
    search_fields = ("email",)
    inlines = [MessageInline]

    def save_formset(self, request, form, formset, change):
        # Before saving messages, set sender='bot' for new messages added by admin
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                # New message added, set sender to 'bot'
                instance.sender = 'bot'
            instance.save()
        formset.save_m2m()
