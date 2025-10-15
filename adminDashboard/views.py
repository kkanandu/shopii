# from django.shortcuts import render,redirect,get_object_or_404
# from django.views.generic import TemplateView,ListView,DetailView,DeleteView,UpdateView
# from django.http import HttpResponseForbidden,JsonResponse
# from django.views import View
# from home.forms import *
# from home.models import *
# from django.utils.decorators import method_decorator
# from django.contrib.auth import authenticate, login, logout
# from django.views.decorators.cache import never_cache
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.urls import reverse_lazy
# from django.db.models import Q
# from django.forms import modelformset_factory
# import json

# # decorator
# def signinrequired(view_func):
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             messages.warning(request, "Please log in first.")
#             return redirect('log')  
#         return view_func(request, *args, **kwargs)
#     return wrapper

# def admin_role_required(view_func):
#     def wrapper(request, *args, **kwargs):
#         if request.user.category not in ['renter', 'seller']:
#             messages.error(request, "You do not have permission to access this page.")
#             return redirect('log')  
#         return view_func(request, *args, **kwargs)
#     return wrapper



# # .....................................................................///.............................

# decorators = [signinrequired, admin_role_required, never_cache]
# @method_decorator(decorators, name='dispatch')
# class AdminDashboard(ListView):
#     template_name = 'admin_dashboard.html'
#     model = Product
#     context_object_name = 'products'  # houses only

#     def get_queryset(self):
#         return Product.objects.filter(user=self.request.user, category='house',transaction_type='rent').order_by('-date')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # context['bike_products'] = Product.objects.filter(user=self.request.user, category='bike').order_by('-date')
#         context['house_rent'] = Product.objects.filter(user=self.request.user, category='house', transaction_type='rent').order_by('-date')
#         context['house_sale'] = Product.objects.filter(user=self.request.user, category='house', transaction_type='buy').order_by('-date')
#         context['bike_rent'] = Product.objects.filter(user=self.request.user, category='bike', transaction_type='rent').order_by('-date')
#         return context

# # class AdminDashboard(ListView):
# #     template_name='admin_dashboard.html'
# #     model = Product
# #     context_object_name = 'products'

# #     def get_queryset(self):
# #         return Product.objects.filter(user=self.request.user)
    

# @method_decorator(decorators, name='dispatch')
# class AddProductView(View):
#     def get(self, request):
#         product_form = ProductForm()
#         image_form = MultipleImageForm()
#         return render(request, 'add_listing.html', {'form': product_form, 'image_form': image_form})

#     def post(self, request):
#         product_form = ProductForm(request.POST, request.FILES)
#         image_form = MultipleImageForm(request.POST, files=request.FILES)

#         if product_form.is_valid() and image_form.is_valid():
#             product = product_form.save(commit=False)
#             product.user = request.user
#             chosen_type = product_form.cleaned_data.get('transaction_type')
#             category = product_form.cleaned_data.get('category')
            
#             if category == 'bike' and chosen_type == 'buy':
#                 messages.warning(request, "Only 'rent' option is allowed for bikes.")
#                 return render(request, 'add_listing.html', {'form': product_form, 'image_form': image_form})


#             # Set transaction_type BEFORE saving
#             if request.user.category == 'seller':
#                 if chosen_type != 'buy':
#                     messages.warning(request, "This feature is not available right now.")
#                     return render(request, 'add_listing.html', {'form': product_form, 'image_form': image_form})
#                 product.transaction_type = 'buy'
#             elif request.user.category == 'renter':
#                 if chosen_type in ['rent', 'buy']:
#                     product.transaction_type = chosen_type
#                 else:
#                     product.transaction_type = 'rent'  # fallback default
#             else:
#                 product.transaction_type = 'rent'
            
#             product.save()  # Save once here

#             images = image_form.cleaned_data.get('images') or request.FILES.getlist('images')
#             for img in images[:5]:
#                 ProductImage.objects.create(product=product, image=img)

#             messages.success(request, "Listing and images uploaded successfully!")
#             return redirect('dash')

#         return render(request, 'add_listing.html', {'form': product_form, 'image_form': image_form})

    



# class EditProductView(View):
#     def get(self, request, pk):
#         product = get_object_or_404(Product, pk=pk, user=request.user)
#         product_form = ProductForm(instance=product)

#         ProductImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, can_delete=True, extra=0)
#         existing_images = ProductImage.objects.filter(product=product)
#         existing_count = existing_images.count()

#         extra_forms = max(0, 5 - existing_count)
#         ProductImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, can_delete=True, extra=extra_forms)

#         formset = ProductImageFormSet(queryset=existing_images)

#         return render(request, 'edit_list.html', {'form': product_form, 'formset': formset})

#     def post(self, request, pk):
#         product = get_object_or_404(Product, pk=pk, user=request.user)
#         product_form = ProductForm(request.POST, request.FILES, instance=product)

#         existing_images = ProductImage.objects.filter(product=product)
#         existing_count = existing_images.count()

#         extra_forms = max(0, 5 - existing_count)
#         ProductImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, can_delete=True, extra=extra_forms)
#         formset = ProductImageFormSet(request.POST, request.FILES, queryset=existing_images)

#         if product_form.is_valid() and formset.is_valid():
#             product_form.save()

#             # Save images
#             instances = formset.save(commit=False)

#             # Handle deletions
#             for obj in formset.deleted_objects:
#                 obj.delete()

#             # Save or update images
#             for instance in instances:
#                 if instance.image:
#                     instance.product = product
#                     instance.save()

#             messages.success(request, "Listing and images updated successfully!")
#             return redirect('dash')

#         return render(request, 'edit_list.html', {'form': product_form, 'formset': formset})

# @login_required
# def delete_product(request, id):
#     product = get_object_or_404(Product, id=id, user=request.user)
#     product.delete()
#     messages.success(request, "Listing deleted successfully!")
#     return redirect('dash')



# class ViewProductList(ListView):
#     template_name = 'products.html'
#     model = Product
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         section = self.request.GET.get('section', 'features')  # default: features
#         # Logic: Pricing shows bikes only; Features shows houses only
#         context['show_bikes'] = section == 'pricing'
#         context['show_houses'] = section == 'features'
        
#         context['house_products'] = Product.objects.filter(category='house').order_by('-date')
#         context['bike_products'] = Product.objects.filter(category='bike').order_by('-date')
#         context['house_rent'] = Product.objects.filter(category='house', transaction_type='rent').order_by('-date')
#         context['house_sale'] = Product.objects.filter(category='house', transaction_type='buy').order_by('-date')
#         context['bike_rent'] = Product.objects.filter(category='bike', transaction_type='rent').order_by('-date')
#         return context
    

# # index.html filter product
# class FilteredHouseTypeView(ListView):
#     model = Product
#     template_name = 'products.html'
#     context_object_name = 'filtered_houses'  # <-- change this to match template

#     def get_queryset(self):
#         house_type = self.kwargs.get('house_type')
#         return Product.objects.filter(category='house', house_type__iexact=house_type).order_by('-date')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['house_type'] = self.kwargs.get('house_type')
#         context['filtered'] = True
#         context['house_rent'] = Product.objects.filter(category='house', transaction_type='rent').order_by('-date')
#         context['house_sale'] = Product.objects.filter(category='house', transaction_type='buy').order_by('-date')
#         context['bike_rent'] = Product.objects.filter(category='bike', transaction_type='rent').order_by('-date')
#         context['bike_sale'] = Product.objects.filter(category='bike', transaction_type='buy').order_by('-date')
#         return context

# # class FilteredHouseTypeView(ListView):
# #     model = Product
# #     template_name = 'products.html'  
# #     context_object_name = 'house_products'

# #     def get_queryset(self):
# #         house_type = self.kwargs.get('house_type')

# #         return Product.objects.filter(category='house', house_type__iexact=house_type).order_by('-date')

# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         context['house_type'] = self.kwargs.get('house_type')
# #         return context


# # class FilteredHouseTypeView(ListView):
# #     model = Product
# #     template_name = 'products.html'
# #     context_object_name = 'house_products'

# #     def get_queryset(self):
# #         house_type = self.kwargs.get('house_type', '')
# #         return Product.objects.filter(house_type__iexact=house_type)
    
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         context['house_type'] = self.kwargs.get('house_type', '')
# #         context['bike_products'] = Product.objects.filter(category='bike').order_by('-date')
# #         return context


# class AdminChatListView(ListView):
#     model = Booking
#     template_name = 'chat.html'
#     context_object_name = 'bookings'

#     def get_queryset(self):
#         return Booking.objects.filter(chat_messages__isnull=False).distinct().order_by('-date_booked')
    
# class AdminChatDetailView(DetailView):
#     model = Booking
#     template_name = 'chat.html'
#     context_object_name = 'booking'

#     def get_object(self):
#         return get_object_or_404(Booking, id=self.kwargs['booking_id'])

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['is_confirmed'] = self.get_object().is_confirmed  # Assuming Booking has this field
#         return context

    

# @login_required
# def send_message(request, booking_id):
#     if request.method == "POST":
#         booking = get_object_or_404(Booking, id=booking_id)
#         message_text = request.POST.get("message")

#         # Only involved user or renter/seller can send
#         if request.user == booking.user or request.user == booking.product.user:
#             ChatMessage.objects.create(
#                 booking=booking,
#                 user=request.user,
#                 message=message_text
#             )

#     return redirect('admin_view_chat_detail', booking_id=booking_id)



# def add_product_view(request):
#     if not request.user.is_active:
#         # user deleted or inactive, logout and redirect
#         logout(request)
#         messages.error(request, "Your account has been deleted or deactivated.")
#         return redirect('log')
    
# # def admin_chat_bookings_view(request):
# #     bookings = Booking.objects.select_related('user', 'product__user').prefetch_related('chat_messages')

# #     return render(request, 'chat.html', {
# #         'bookings': bookings
# #     })

# from django.db.models import OuterRef, Subquery,Max
# from home.models import Booking, ChatMessage
# def admin_chat_bookings_view(request):
#     user = request.user

#     # Step 1: Get latest booking per user (as owner)
#     latest_bookings = (
#         Booking.objects
#         .filter(product__user=user)
#         .values('user')  # Group by booking user
#         .annotate(latest_booking_id=Max('id'))  # Get latest booking per user
#     )

#     booking_ids = [b['latest_booking_id'] for b in latest_bookings]

#     # Step 2: Use those IDs to get booking and latest chat info
#     latest_messages = ChatMessage.objects.filter(
#         booking=OuterRef('pk')
#     ).order_by('-timestamp')

#     bookings = (
#         Booking.objects
#         .filter(id__in=booking_ids)
#         .select_related('user', 'product__user')
#         .annotate(
#             last_msg_content=Subquery(latest_messages.values('content')[:1]),
#             last_msg_sender=Subquery(latest_messages.values('sender__username')[:1]),
#             last_msg_time=Subquery(latest_messages.values('timestamp')[:1])
#         )
#     )

#     return render(request, 'chat.html', {
#         'bookings': bookings
#     })
# # def admin_chat_bookings_view(request):
# #     user = request.user

# #     latest_messages = ChatMessage.objects.filter(
# #         booking=OuterRef('pk')
# #     ).order_by('-timestamp')
# #     bookings = Booking.objects.filter(
# #         Q(product__user=user)
# #     ).select_related('user', 'product__user').annotate(
# #     # bookings = Booking.objects.select_related('user', 'product__user').annotate(
# #         last_msg_content=Subquery(latest_messages.values('content')[:1]),
# #         last_msg_sender=Subquery(latest_messages.values('sender__username')[:1]),
# #         last_msg_time=Subquery(latest_messages.values('timestamp')[:1])
# #     )

# #     return render(request, 'chat.html', {
# #         'bookings': bookings
# #     })


# @login_required
# def my_chat_bookings_view(request):
#     user = request.user

#     latest_messages = ChatMessage.objects.filter(
#         booking=OuterRef('pk')
#     ).order_by('-timestamp')

#     bookings = Booking.objects.filter(Q(user=user) | Q(product__user=user)).select_related('product__user').annotate(
#         last_msg_content=Subquery(latest_messages.values('content')[:1]),
#         last_msg_sender=Subquery(latest_messages.values('sender__username')[:1]),
#         last_msg_time=Subquery(latest_messages.values('timestamp')[:1])
#     )

#     return render(request, 'my_chat_view.html', {
#         'bookings': bookings
#     })


# def rental_history_view(request):
#     paid_bookings = Booking.objects.filter(is_paid=True).select_related('user', 'product')
    
#     return render(request, 'rental_history.html', {
#         'bookings': paid_bookings
#     })




