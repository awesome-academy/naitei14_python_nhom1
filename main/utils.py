from django.core.mail import send_mail
from django.conf import settings
from .constants import (
    EMAIL_SUBJECT_BOOKING_CONFIRMATION,
    EMAIL_SUBJECT_BOOKING_APPROVED,
    EMAIL_SUBJECT_BOOKING_REJECTION,
    EMAIL_SUBJECT_BOOKING_CANCELLATION,
    EMAIL_TEMPLATE_BOOKING_CONFIRMATION,
    EMAIL_TEMPLATE_BOOKING_APPROVED,
    EMAIL_TEMPLATE_BOOKING_REJECTION,
    EMAIL_TEMPLATE_BOOKING_CANCELLATION,
)


def send_booking_email(
        booking,
        subject_template,
        message_template,
        extra_context=None):
    """
    Hàm gửi email tái sử dụng cho tất cả loại thông báo booking.
    """
    try:
        context = {
            "user_name": booking.user.get_full_name(),
            "pitch_name": booking.pitch.name,
            "booking_date": booking.booking_date.strftime('%d/%m/%Y'),
            "time_slot_name": booking.time_slot.time_slot.name,
            "start_time": booking.time_slot.time_slot.start_time.strftime('%H:%M'),
            "end_time": booking.time_slot.time_slot.end_time.strftime('%H:%M'),
            "final_price": f"{booking.final_price:,.0f}"}

        if extra_context:
            context.update(extra_context)

        subject = subject_template.format(booking_id=booking.id)
        message = message_template.format(**context)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Send mail error: {e}")
        return False


def send_booking_confirmation_email(booking):
    return send_booking_email(
        booking,
        EMAIL_SUBJECT_BOOKING_CONFIRMATION,
        EMAIL_TEMPLATE_BOOKING_CONFIRMATION
    )


def send_booking_approved_email(booking):
    return send_booking_email(
        booking,
        EMAIL_SUBJECT_BOOKING_APPROVED,
        EMAIL_TEMPLATE_BOOKING_APPROVED
    )


def send_booking_rejection_email(
        booking,
        reason="Khung giờ đã có người đặt hoặc sân không khả dụng."):
    return send_booking_email(
        booking,
        EMAIL_SUBJECT_BOOKING_REJECTION,
        EMAIL_TEMPLATE_BOOKING_REJECTION,
        extra_context={"reason": reason}
    )


def send_booking_cancellation_email(booking):
    return send_booking_email(
        booking,
        EMAIL_SUBJECT_BOOKING_CANCELLATION,
        EMAIL_TEMPLATE_BOOKING_CANCELLATION
    )


def format_price(price):
    """
    Format giá tiền theo định dạng VN

    Args:
        price: Decimal hoặc float

    Returns:
        str: "1,000,000đ"
    """
    return f"{price:,.0f}đ"


def format_datetime_vn(dt):
    """
    Format datetime theo định dạng VN

    Args:
        dt: datetime object

    Returns:
        str: "Thứ Hai, 15/01/2024 14:30"
    """
    days = {
        0: 'Thứ Hai',
        1: 'Thứ Ba',
        2: 'Thứ Tư',
        3: 'Thứ Năm',
        4: 'Thứ Sáu',
        5: 'Thứ Bảy',
        6: 'Chủ Nhật',
    }
    day_name = days[dt.weekday()]
    return f"{day_name}, {dt.strftime('%d/%m/%Y %H:%M')}"
