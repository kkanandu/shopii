from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView,ListView,DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.db.models import Q
from home.models import *
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from .forms import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.http import JsonResponse, Http404
User = get_user_model()



class Home(ListView):
    template_name = 'index.html'
    model = Product
    context_object_name = 'products'


    def get_queryset(self):
        # Show recent house listings (limit 3)
        return Product.objects.filter(category='house').order_by('-date')[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # House for Rent
        context['house_rent'] = Product.objects.filter(category='house', transaction_type='rent').order_by('-date')
        
        # House for Sale (buy)
        context['house_sale'] = Product.objects.filter(category='house', transaction_type='buy').order_by('-date')
        
        # Bike for Rent
        context['bike_rent'] = Product.objects.filter(category='bike', transaction_type='rent').order_by('-date')
        
        # Bike for Sale (buy) if applicable
        context['bike_sale'] = Product.objects.filter(category='bike', transaction_type='buy').order_by('-date')

        # Latest bike products (limit 3)
        context['bike_products'] = Product.objects.filter(category='bike').order_by('-date')[:3]

         # Best renters (top 5 users whose products were booked the most)
        User = get_user_model()
        top_renters = (
            User.objects
            .annotate(total_bookings=Count('product__product_bookings'))
            .filter(total_bookings__gt=0)
            .order_by('-total_bookings')[:5]
        )
        context['top_renters'] = top_renters


        return context



@login_required
def profile_view(request):
    report_form = ReportForm()
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')  # Always define
    replied_reports = Report.objects.filter(user=request.user).exclude(admin_reply__isnull=True).exclude(admin_reply__exact='').order_by('-replied_at')
    if request.method == 'POST':
        delete_id = request.POST.get("delete_complaint_id")
        if delete_id:
            complaint_to_delete = get_object_or_404(Complaint, pk=delete_id, user=request.user)
            complaint_to_delete.delete()
            messages.success(request, "Complaint deleted successfully.")
            return redirect('profile') 
        
        if 'submit_report' in request.POST:
            report_form = ReportForm(request.POST)
            if report_form.is_valid():
                new_report = report_form.save(commit=False)
                new_report.user = request.user
                new_report.save()
                messages.success(request, "Report sent to admin successfully.")
                return redirect('profile')
            else:
                print(report_form.errors)  # Add this line to see errors in the console/log
                messages.error(request, "Please correct the errors in the report form.")

        else:
            report_form = ReportForm()

        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
        complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
        
    return render(request, 'profile.html', {'form': form,'complaints': complaints,'report_form': report_form,  'replied_reports': replied_reports,  })

@login_required
def profile_edit_view(request):
    print("profile_edit_view reached")  # Check your console/logs

    if request.method == 'POST':
        form = ProfileForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


@login_required
def add_to_wishlist(request, **kwargs):
    product_id = kwargs.get('id')
    product = get_object_or_404(Product, id=product_id)

    if not Wishlist.objects.filter(user=request.user, product=product).exists():
        Wishlist.objects.create(user=request.user, product=product)

    return redirect('wishlist_list')  # Redirect to wishlist list page after adding


@login_required
def remove_from_wishlist(request, **kwargs):
    product_id = kwargs.get('id')
    wishlist_item = Wishlist.objects.filter(user=request.user, product_id=product_id).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, "Property removed from wishlist.")
    else:
        messages.warning(request, "property was not found in your wishlist.")

    return redirect('wishlist_list')  # Redirect to wishlist list page after removing


@login_required
def wishlist_list(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'add_to_wishlist.html', {'wishlist_items': wishlist_items})


class ProductDetailView(DetailView):
    model = Product
    template_name = 'cart.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        product.refresh_from_db()
        context['images'] = product.images.all()
        total_booked = Booking.objects.filter(product=product).count()
        context['remaining_slots'] = max(product.booking_limit - total_booked, 0)
        context['review_form'] = ReviewForm()
        context['reviews'] = Review.objects.filter(product=product).select_related('user').order_by('-posted_at')
        editing_review_id = self.request.GET.get('edit')
        if editing_review_id:
         context['editing_review_id'] = editing_review_id
        return context
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')

        # Delete review
        if action == 'delete':
            review_id = request.POST.get('review_id')
            review = Review.objects.filter(id=review_id, user=request.user).first()
            if review:
                review.delete()
                messages.success(request, "Review deleted successfully.")
            else:
                messages.warning(request, "You cannot delete this review.")
            return redirect('detailview', pk=self.object.pk)

        # Edit review
        if action == 'edit':
            review_id = request.POST.get('review_id')
            review = Review.objects.filter(id=review_id, user=request.user).first()
            if not review:
                messages.warning(request, "You cannot edit this review.")
                return redirect('detailview', pk=self.object.pk)

            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                messages.success(request, "Review updated successfully.")
                return redirect('detailview', pk=self.object.pk)
            else:
                # Form invalid: render page with form errors on this review only
                context = self.get_context_data()
                context['review_form'] = form
                context['editing_review_id'] = review_id
                return self.render_to_response(context)

        # Add new review (existing code)
        existing_review = Review.objects.filter(product=self.object, user=request.user).first()
        if existing_review:
            messages.warning(request, "You have already reviewed this product.")
            return redirect('detailview', pk=self.object.pk)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = self.object
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('detailview', pk=self.object.pk)

        context = self.get_context_data()
        context['review_form'] = form
        return self.render_to_response(context)



import razorpay
def confirm_booking(request, booking_id):
    # Fetch the booking instance
    booking = get_object_or_404(Booking, id=booking_id)

    # Authorization check
    if request.user != booking.user and request.user != booking.product.user:
        return render(request, "booking.html")

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


    # Define amount (hardcoded ₹500 for example, in paise)
    amount_paise = 50000

    # Create Razorpay order
    DATA = {
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"receipt_{booking.id}",
        "notes": {
            "booking_id": str(booking.id),
            "user": request.user.username,
        }
    }

    razorpay_order = client.order.create(data=DATA)

    # Save the order ID to the booking instance (if your model has this field)
    booking.razorpay_order_id = razorpay_order['id']
    booking.save()

    # Prepare context for template
    context = {
    "booking": booking,
    "is_confirmed": booking.is_confirmed,
    "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    "order_id": razorpay_order["id"],
    "amount": amount_paise,
    }

    return render(request, "booking.html", context)


@login_required
def book_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if user has an active non-expired unpaid booking
    existing_booking = Booking.objects.filter(user=request.user, product=product, is_active=True, is_paid=False).last()
    if existing_booking and not existing_booking.is_expired():
        booking = existing_booking
    else:
        if product.available_slots() <= 0:
            messages.warning(request, "Sorry, no slots available at the moment.")
            return redirect('home')

        # Create temporary booking (reserved)
        booking = Booking.objects.create(
            user=request.user,
            product=product,
            is_confirmed=False,
            is_paid=False,
            reserved_at=timezone.now(),
            is_active=True
        )

    return render(request, 'booking.html', {
        'product': product,
        'booking': booking,
        'is_confirmed': booking.is_confirmed,
    })

def search_results(request):
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('search_type', '').lower()

    if query and search_type == 'feature':  # Searching houses
        filtered_houses = Product.objects.filter(
            Q(category__icontains='house') & Q(location__icontains=query)
        )
        context = {
            'filtered': True,
            'filtered_houses': filtered_houses,
            'search_type': 'house',  # Send 'house' here to match template
            'query': query,
        }

    elif query and search_type == 'pricing':  # Searching bikes
        filtered_bikes = Product.objects.filter(
            Q(category__icontains='bike') & Q(location__icontains=query)
        )
        context = {
            'filtered': True,
            'filtered_bikes': filtered_bikes,
            'search_type': 'bike',  # Send 'bike' here to match template
            'query': query,
        }

    else:
        # Default / no filter - show all categories
        house_rent = Product.objects.filter(category__iexact='House Rent')
        house_sale = Product.objects.filter(category__iexact='House Sale')
        bike_rent = Product.objects.filter(category__iexact='Bike Rent')
        context = {
            'filtered': False,
            'house_rent': house_rent,
            'house_sale': house_sale,
            'bike_rent': bike_rent,
        }

    return render(request, 'products.html', context)
    






from django.urls import reverse

def complaint_about_property(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    owner = product.user

    if request.method == 'POST':
        form = ComplaintForm(request.POST)  # ✅ Correct usage
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.owner = owner
            complaint.product = product
            complaint.house_type = product.house_type  # ✅ Overwrite to ensure accuracy
            complaint.save()
            messages.success(request, "Complaint about property submitted successfully.")
            return redirect(reverse('complaint_about_property', kwargs={'product_id': product_id}))
    else:
        form = ComplaintForm(initial={'house_type': product.house_type})  # ✅ Only for GET

    return render(request, 'complaints.html', {
        'form': form,
        'product': product,
        'owner': owner,
        'show_property_details': True,
    })



def complaints_about_owner_view(request, owner_id):
    owner = get_object_or_404(User, pk=owner_id)
    complaints = Complaint.objects.filter(owner=owner).order_by('-created_at')

    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        reply_text = request.POST.get("reply")

        delete_id = request.POST.get("delete_complaint_id")

        if delete_id:
            complaint_to_delete = get_object_or_404(Complaint, pk=delete_id, owner=owner)
            complaint_to_delete.delete()
            messages.success(request, "Complaint deleted successfully.")
            return redirect(request.path_info)

        if complaint_id and reply_text:
            complaint = get_object_or_404(Complaint, pk=complaint_id, owner=owner)
            complaint.reply = reply_text
            complaint.is_resolved = True
            complaint.save()
            messages.success(request, "Reply submitted successfully.")
            return redirect(request.path_info)

    return render(request, 'complaint_view.html', {
        'owner': owner,
        'complaints': complaints,
    })


def complaint_about_admin(request):
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        messages.error(request, "No admin found.")
        return redirect('home')

    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.owner = admin_user
            complaint.product = None
            complaint.complaint_type = 'admin'
            complaint.house_type = None
            complaint.save()
            messages.success(request, "Complaint to admin submitted successfully.")
            return redirect('home')
    else:
        form = ComplaintForm()  # no initial

    return render(request, 'complaints.html', {
        'form': form,
        'owner': admin_user,
        'show_property_details': False,
        'is_admin_complaint': True,
    })


def notification_detail(request, notification_id):
    try:
        notification = Notification.objects.get(pk=notification_id, user=request.user)
    except Notification.DoesNotExist:
        raise Http404("Notification not found")

    if not notification.is_read:
        notification.is_read = True
        notification.save()

    return JsonResponse({
        "message": notification.message,
        "created_at": notification.created_at.strftime('%B %d, %Y %H:%M')
    })
def notification_delete(request, notification_id):
    print(f"DEBUG: Received delete request for notification id={notification_id}, method={request.method}")
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=notification_id)
        # Optional: check if user has rights to delete this notification
        if notification.user != request.user:
            return HttpResponseForbidden()
        notification.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request method"}, status=405)



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatSession, Message

@csrf_exempt
def save_email(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            if not email:
                return JsonResponse({"error": "Email required"}, status=400)
            
            # Create new chat session with unique UUID
            chat_session = ChatSession.objects.create(email=email)
            return JsonResponse({"session_id": str(chat_session.session_id)})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def save_issue(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        issue = data.get('issue')
        if not session_id or not issue:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        session = get_object_or_404(ChatSession, session_id=session_id)

        # Save message related to the session
        Message.objects.create(
            session=session,
            sender='user',
            content=issue
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid method'}, status=405)


def get_messages(request, session_id):
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Invalid session'}, status=400)

    messages = session.messages.order_by('timestamp').values('sender', 'content', 'timestamp')
    return JsonResponse({'messages': list(messages)})

# def search_results(request):
#     query = request.GET.get('query', '').strip()
#     search_type = request.GET.get('search_type', 'feature')  # default to feature if not provided

#     if query:
#         if search_type == 'feature':
#             # Search houses (both rent and sale)
#             filtered_houses = Product.objects.filter(
#                 Q(category='house'),
#                 Q(location__icontains=query)
#             ).order_by('-date')

#             context = {
#                 'filtered': True,
#                 'filtered_houses': filtered_houses,
#                 'house_type': query,
#                 'show_houses': True,
#                 'show_bikes': False,
#             }

#         elif search_type == 'pricing':
#             # Search bikes for rent only
#             filtered_bikes = Product.objects.filter(
#                 category='bike',
#                 transaction_type='rent',
#                 location__icontains=query
#             ).order_by('-date')

#             context = {
#                 'filtered': True,
#                 'filtered_bikes': filtered_bikes,
#                 'bike': query,
#                 'show_houses': False,
#                 'show_bikes': True,
#             }

#         else:
#             # Fallback, treat as feature
#             filtered_houses = Product.objects.filter(
#                 Q(category='house'),
#                 Q(location__icontains=query)
#             ).order_by('-date')

#             context = {
#                 'filtered': True,
#                 'filtered_houses': filtered_houses,
#                 'house_type': query,
#                 'show_houses': True,
#                 'show_bikes': False,
#             }

#     else:
#         # No query: show default listings
#         house_rent = Product.objects.filter(category='house', transaction_type='rent').order_by('-date')
#         house_sale = Product.objects.filter(category='house', transaction_type='buy').order_by('-date')
#         bike_rent = Product.objects.filter(category='bike', transaction_type='rent').order_by('-date')

#         context = {
#             'filtered': False,
#             'house_rent': house_rent,
#             'house_sale': house_sale,
#             'bike_rent': bike_rent,
#             'show_houses': True,
#             'show_bikes': True,
#         }

#     return render(request, 'products.html', context)

# def search_results(request):
#     query = request.GET.get('query', '').strip()  # ✅ Define the query

#     if query:
#         filtered_houses = Product.objects.filter(
#             Q(category__icontains='house') & Q(location__icontains=query) |
#             Q(category__icontains='bike') & Q(location__icontains=query)
#         )

#         context = {
#             'filtered': True,
#             'filtered_houses': filtered_houses,
#             'house_type': query,  # You use this in your template heading
#             'bike': query,  # You use this in your template heading
#         }
#     else:
#         house_rent = Product.objects.filter(category__iexact='House Rent')
#         house_sale = Product.objects.filter(category__iexact='House Sale')
#         bike_rent = Product.objects.filter(category__iexact='Bike Rent')

#         context = {
#             'filtered': False,
#             'house_rent': house_rent,
#             'house_sale': house_sale,
#             'bike_rent': bike_rent,
#         }

#     return render(request, 'products.html', context)


def demo(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    product = booking.product
    amount = product.price * 100  # Razorpay expects amount in paise

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    context = {
        'booking': booking,
        'product': product,
        'user': request.user,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'payment_id': payment['id'],
        'csrf_token': get_token(request),
    }

    return render(request, 'demo.html', context)

#payment view
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('product').order_by('-reserved_at')
    return render(request, 'view_my_order_bookings.html', {'bookings': bookings})

@csrf_exempt
def payment_callback(request, booking_id):
    if request.method == "POST":
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            data = request.POST
            client.utility.verify_payment_signature({
                "razorpay_order_id": data.get("razorpay_order_id"),
                "razorpay_payment_id": data.get("razorpay_payment_id"),
                "razorpay_signature": data.get("razorpay_signature"),
            })

            booking = get_object_or_404(Booking, id=booking_id)
            booking.is_paid = True
            booking.save()

            return JsonResponse({"status": "success"})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "error", "error": "Invalid payment signature"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)}, status=400)
    return JsonResponse({"status": "error", "error": "Invalid request method"}, status=405)

def success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.is_paid:
        return render(request, "success.html", {"booking": booking})
    else:
        return HttpResponseForbidden("You are not allowed to view this page. Payment not completed.")


@login_required
def chat_room(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)

    # Find booking in either direction (renter/owner or owner/renter)
    booking = Booking.objects.filter(
        Q(user=request.user, product__user=receiver) |
        Q(user=receiver, product__user=request.user)
    ).first()

    if request.method == 'POST':
        message_text = request.POST.get('message')
        booking_id = request.POST.get('booking_id')

        if message_text and booking_id:
            booking_instance = get_object_or_404(Booking, id=booking_id)
            ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                content=message_text,
                booking=booking_instance
            )
            return redirect('chat_room', receiver_id=receiver.id)

    messages = ChatMessage.objects.filter(
        sender__in=[request.user, receiver],
        receiver__in=[request.user, receiver]
    ).order_by('timestamp')

    return render(request, 'chat_room.html', {
        'receiver': receiver,
        'messages': messages,
        'booking': booking
    })



@login_required
def submit_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Prevent duplicate review by same user (optional logic)
            Review.objects.filter(user=request.user, product=product).delete()

            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
    
    return redirect('product_detail', pk=pk)

# def rate_product(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)

#     if request.method == 'POST' and request.user.is_authenticated:
#         value = int(request.POST.get('value'))
#         if 1 <= value <= 5:
#             rating_obj, created = Rating.objects.update_or_create(
#                 product=product,
#                 user=request.user,
#                 defaults={'value': value}
#             )

#             # Update product average rating
#             all_ratings = product.user_ratings.all()
#             avg_rating = round(sum(r.value for r in all_ratings) / all_ratings.count(), 1)
#             product.rating = avg_rating
#             product.save()

#     return redirect('detailview', pk=product.id)






# def chat_room(request, receiver_id):
#     receiver = get_object_or_404(User, id=receiver_id)

#     # Fetch chat messages between the current user and the receiver
#     messages = ChatMessage.objects.filter(
#         sender__in=[request.user, receiver],
#         receiver__in=[request.user, receiver]
#     ).order_by('timestamp')

#     return render(request, 'chat_room.html', {
#         'receiver': receiver,
#         'messages': messages
#     })


# @login_required
# def booking_page(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     booking = Booking.objects.filter(user=request.user, product=product).first()
#     if not booking:
#         messages.warning(request, "You must book this product first.")
#         return redirect('detailview', pk=product_id)

#     return render(request, 'booking.html', {
#         'product': product,
#         'booking': booking,
#         'is_confirmed': booking.is_confirmed,
#     })





# def booking_view(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user)
#     context = {
#         'booking': booking,
#         'is_confirmed': booking.is_confirmed,
#     }
#     return render(request, 'booking.html', context)


# @login_required
# def send_message(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id)
#     # Ensure the user is either the renter or the user who booked
#     if request.user != booking.user and request.user != booking.product.user:
#         return HttpResponseForbidden("Not allowed to send message.")

#     if request.method == 'POST':
#         message_text = request.POST.get('message')
#         if message_text:
#             ChatMessage.objects.create(
#                 booking=booking,
#                 user=request.user,
#                 message=message_text,
#                 timestamp=timezone.now()
#             )
#     return redirect('booking_view', booking_id=booking.id)

# @login_required
# def chat_room(request, room_name):
#     search_query = request.GET.get('search', '') 
#     users = User.objects.exclude(id=request.user.id) 
#     chats = ChatMessage.objects.filter(
#         (Q(sender=request.user) & Q(receiver__username=room_name)) |
#         (Q(receiver=request.user) & Q(sender__username=room_name))
#     )

#     if search_query:
#         chats = chats.filter(Q(content__icontains=search_query))  

#     chats = chats.order_by('timestamp') 
#     user_last_messages = []

#     for user in users:
#         last_message = ChatMessage.objects.filter(
#             (Q(sender=request.user) & Q(receiver=user)) |
#             (Q(receiver=request.user) & Q(sender=user))
#         ).order_by('-timestamp').first()

#         user_last_messages.append({
#             'user': user,
#             'last_message': last_message
#         })

#     # Sort user_last_messages by the timestamp of the last_message in descending order
#     user_last_messages.sort(
#         key=lambda x: x['last_message'].timestamp if x['last_message'] else None,
#         reverse=True
#     )

#     return render(request, 'chat.html', {
#         'room_name': room_name,
#         'chats': chats,
#         'users': users,
#         'user_last_messages': user_last_messages,
#         'search_query': search_query 
#     })



def show_order_template(request):
    return render(request, 'order.html')
def cart(request):
    return render(request, 'cartchange.html')