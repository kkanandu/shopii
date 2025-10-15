# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import *
# from django.urls import path
# from django.contrib import messages
# from django.shortcuts import render, redirect,get_object_or_404
# from django.utils.html import format_html

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     list_display = ['username', 'email', 'approved_status', 'staff_status', 'delete_link']
#     list_filter = [ 'is_approved', 'is_staff']
#     actions = ['approve_users']

#     def approve_users(self, request, queryset):
#         updated = 0
#         for user in queryset:
#             if user.category in ['seller', 'renter'] and not user.is_approved:
#                 user.is_approved = True
#                 user.save()
#                 updated += 1
#         self.message_user(request, f"{updated} users approved.")

#     def has_delete_permission(self, request, obj=None):
#         if obj is not None and obj == request.user:
#             return False
#         return super().has_delete_permission(request, obj)

#     def get_actions(self, request):
#         actions = super().get_actions(request)
#         if 'delete_selected' in actions:
#             def delete_selected_with_check(modeladmin, request, queryset):
#                 if request.user in queryset:
#                     self.message_user(request, "You cannot delete your own account.", level=messages.ERROR)
#                     return
#                 return admin.actions.delete_selected(modeladmin, request, queryset)
#             actions['delete_selected'] = (delete_selected_with_check, 'delete_selected', 'Delete selected users')
#         return actions

#     def delete_model(self, request, obj):
#         obj.deletion_reason = "Deleted via admin without reason"
#         obj.is_approved = False 
#         obj.save()
#         super().delete_model(request, obj)

#     def delete_link(self, obj):
#         return format_html(
#             '<a class="button" href="{}">Delete with Reason</a>',
#             f'{obj.pk}/delete-with-reason/'
#         )
#     delete_link.short_description = 'Delete with Reason'
#     delete_link.allow_tags = True

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('<int:user_id>/delete-with-reason/', self.admin_site.admin_view(self.delete_with_reason_view), name='delete_with_reason'),

#         ]
#         return custom_urls + urls
#     def delete_with_reason_view(self, request, user_id):
#         user = get_object_or_404(CustomUser, pk=user_id)

#         if request.method == 'POST':
#             reason = request.POST.get('reason')
#             user.deletion_reason = reason
#             user.is_deleted = True
#             user.is_active = False  
#             user.is_approved = False
#             user.save()
#             self.message_user(request, f"User {user.username} marked as deleted with reason.")
#             return redirect('admin:accounts_customuser_changelist')


#         return render(request, 'delete_with_reason.html', {'user': user})

#     def approved_status(self, obj):
#         return obj.is_approved
#     approved_status.boolean = True
#     approved_status.short_description = 'Approved'

#     def staff_status(self, obj):
#         return obj.is_staff
#     staff_status.boolean = True
#     staff_status.short_description = 'Staff'