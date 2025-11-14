from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ===== Enum ===================================================
class Role(models.TextChoices):
    USER = "User", "User"
    ADMIN = "Admin", "Admin"
    GUEST = "Guest", "Guest"


class BookingStatus(models.TextChoices):
    PENDING = "Pending", "Đang chờ xác nhận"
    CONFIRMED = "Confirmed", "Đã xác nhận"
    REJECTED = "Rejected", "Bị từ chối"
    CANCELLED = "Cancelled", "Người dùng hủy"


# ===== User ===================================================
class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)

    # Activation
    activation_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    activation_expiry = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


# ===== Pitch ===================================================
class PitchType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Pitch(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    pitch_type = models.ForeignKey(PitchType, on_delete=models.CASCADE, related_name="pitches")
    base_price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.JSONField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.address}"


# ===== Voucher ===================================================
class Voucher(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    discount_percent = models.PositiveIntegerField(default=0)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


# ===== Booking ===================================================
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, related_name="bookings")

    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2)

    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    voucher = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True, blank=True)

    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=BookingStatus.choices, default=BookingStatus.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ===== Review ===================================================
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, related_name="reviews")

    rating = models.IntegerField()
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ===== Comment ===================================================
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ===== Favorite ===================================================
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, related_name="favorited_by")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "pitch")  # Không cho 1 user thích 1 sân 2 lần
