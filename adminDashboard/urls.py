from django.urls import path
# from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('dash',AdminDashboard.as_view(),name='dash'),
    # path('product',AddProductView.as_view(),name='product'),
    # path('edit_product/<int:pk>',EditProductView.as_view(),name='edit_product'),
    # path('delete_product/<int:id>',delete_product,name='delete_product'),
    # path('productview',ViewProductList.as_view(),name='productview'),
    # path('house-type/<str:house_type>/', FilteredHouseTypeView.as_view(), name='filter_by_house_type'),
    # path('chats/', AdminChatListView.as_view(), name='admin_view_chats'),
    # path('chats/<int:booking_id>/', AdminChatDetailView.as_view(), name='admin_view_chat_detail'),
    # path('chat-bookings/', admin_chat_bookings_view, name='admin_chat_bookings'),
    # path('my_chat_view/', my_chat_bookings_view, name='my_chat_view'),
    # path('rental-history', rental_history_view, name='rental_history'),





]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
