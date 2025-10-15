from django.db import models
from django.utils.timesince import timesince
from django.utils import timezone
from datetime import timedelta


from django.conf import settings

# Create your models here.
CATEGORY = (
    ('house', 'House'),
    ('bike', 'Bike'),
)
HOUSE_TYPE_CHOICES = (
    ('family', 'Family House'),
    ('apartment', 'Apartment'),
    ('cottage', 'Luxury Cottage'),
    ('hostel', 'Hostel'),
    ('resort', 'Resort'),
    ('lodge', 'Lodge'),
)
TRANSACTION_TYPE_CHOICES = (
    ('buy', 'Buy'),
    ('rent', 'Rent'),
)
class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=CATEGORY)
    house_type = models.CharField(max_length=20,choices=HOUSE_TYPE_CHOICES,blank=True, null=True,help_text="Only required if category is House" )
    product_image = models.ImageField(upload_to='product_images')
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    location = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    def posted_ago(self):
        delta = timezone.now() - self.date

        if delta.days >= 1:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        hours = delta.seconds // 3600
        if hours >= 1:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        minutes = (delta.seconds % 3600) // 60
        if minutes >= 1:
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        return "Just now"

    rating = models.FloatField(default=0.0)
    description = models.TextField()
    booking_limit = models.PositiveIntegerField(default=1)
    transaction_type = models.CharField(max_length=10,choices=TRANSACTION_TYPE_CHOICES,default='rent')

    def available_slots(self):
        # Expire old bookings first
        expired_bookings = self.product_bookings.filter(
            is_active=True,
            is_paid=False,
            reserved_at__lt=timezone.now() - timedelta(minutes=15)
        )
        expired_bookings.update(is_active=False)

        active_count = self.product_bookings.filter(is_active=True).count()
        return self.booking_limit - active_count
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE,)
    image = models.ImageField(upload_to='product_images') 



class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_bookings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_bookings')
    date_booked = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)  # renter confirmation
    is_active = models.BooleanField(default=True)  # if slot is still active (temp hold or confirmed)
    is_paid = models.BooleanField(default=False)
    reserved_at = models.DateTimeField(default=timezone.now)


    def is_expired(self):
        return timezone.now() > self.reserved_at + timedelta(minutes=15)


class ChatMessage(models.Model):
    booking = models.ForeignKey(
        'Booking', 
        related_name='chat_messages',
        on_delete=models.CASCADE,
        null=True,  
        blank=True
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="messages_sent",
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="messages_received",
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp'] 
    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)


# class Rating(models.Model):
#     product = models.ForeignKey(Product, related_name='user_ratings', on_delete=models.CASCADE)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     value = models.IntegerField()  # between 1 and 5
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('product', 'user')  # Prevent multiple ratings per user

#     def __str__(self):
#         return f"{self.user.username} rated {self.product.title}: {self.value} stars"


class Complaint(models.Model):
    HOUSE_TYPE_CHOICES = (
        ('family', 'Family House'),
        ('apartment', 'Apartment'),
        ('cottage', 'Luxury Cottage'),
        ('hostel', 'Hostel'),
        ('resort', 'Resort'),
        ('lodge', 'Lodge'),
    )


    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints_made')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, blank=True, null=True, related_name='complaints')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints_received')
    house_type = models.CharField(max_length=20, choices=HOUSE_TYPE_CHOICES, blank=True, null=True, help_text="Select house type if applicable")
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    admin_reply = models.TextField(blank=True, null=True)  # admin reply field
    replied_at = models.DateTimeField(blank=True, null=True) 

    def __str__(self):
        return f"Report by {self.user.username} - {self.subject}"
    

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # New field!

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at


import uuid

class ChatSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({self.session_id})"

class Message(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot'),
    )
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.title()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"



class Review(models.Model):
    SENTIMENT_CHOICES = (
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)  # ⭐ Star rating 1-5
    text = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    posted_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Automatically assign sentiment based on rating
        if self.rating == 1:
            self.sentiment = 'negative'
        elif self.rating == 5:
            self.sentiment = 'positive'
        else:
            self.sentiment = 'neutral'
        super().save(*args, **kwargs)

    