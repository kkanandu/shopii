from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('home',Home.as_view(),name='home'),
    path('profile',profile_view,name='profile'),
    path('editprofile',profile_edit_view,name='editprofile'),
    path('detailview/<int:pk>/',ProductDetailView.as_view(),name='detailview'),
    path('order/', show_order_template, name='order'),
    path('cart/', cart, name='cart'),
    
  # ✅ Add to wishlist
    path('wishlist/add/<int:id>/', add_to_wishlist, name='add_to_wishlist'),

    # ✅ Remove from wishlist
    path('wishlist/remove/<int:id>/', remove_from_wishlist, name='remove_from_wishlist'),

    # ✅ View wishlist
    path('wishlist/', wishlist_list, name='wishlist_list'),
    path('book/<int:booking_id>/', confirm_booking, name='confirm_booking'),
    path('book/<int:product_id>', book_product, name='book_product'),
    path('search_results',search_results, name='search_results'),
    path('demo/<int:booking_id>/', demo, name='demo'),
    path('my-bookings/',my_bookings, name='my_bookings'),
    path('payment-callback/<int:booking_id>/', payment_callback, name='payment_callback'),
    path('success/<int:booking_id>/', success, name='success'),
    path('chat/<int:receiver_id>/', chat_room, name='chat_room'),
    # path('rate-product/<int:product_id>/', rate_product, name='rate_product'),
    path('complaint/admin/', complaint_about_admin, name='complaint_about_admin'),


    # Complaint about an owner (not product specific)
     path('complaints/owner/<int:owner_id>/', complaints_about_owner_view, name='complaints_about_owner_list'),

# urls.py
    path('notification/<int:notification_id>/',notification_detail, name='notification_detail'),
    path('notification/<int:notification_id>/delete/',notification_delete, name='notification_delete'),

    # Complaint about property (pass product id)
    path('complaint/property/<int:product_id>/', complaint_about_property, name='complaint_about_property'),
    path('save-email/', save_email, name='save_email'),
    path('save-issue/', save_issue, name='save_issue'),
path('get-messages/<uuid:session_id>/', get_messages, name='get_messages'),



      # path('chat', chat_room, name='chat_room'),

  #  path('success/<int:booking_id>/', success, name='success'),

  #  path('payment-callback/<int:booking_id>/',payment_callback, name='payment_callback'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
