import logging
from smtplib import SMTPException
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
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import secrets
import string
import textwrap


def generate_activation_token():
    return secrets.token_urlsafe(24)


def send_activation_email(user, request):
    user.activation_token = generate_activation_token()
    user.activation_expiry = timezone.now() + timedelta(
        hours=settings.ACTIVATION_TOKEN_EXPIRY_HOURS
    )
    user.save()

    activation_link = request.build_absolute_uri(
        f'/activate/{user.activation_token}/'
    )

    subject = 'Xác thực tài khoản của bạn'
    message = textwrap.dedent(f"""
        Xin chào {user.full_name},

        Vui lòng nhấp vào liên kết dưới đây để xác thực tài khoản của bạn:
        {activation_link}

        Liên kết này sẽ hết hạn sau {settings.ACTIVATION_TOKEN_EXPIRY_HOURS} giờ.

        Nếu bạn không tạo tài khoản này, vui lòng bỏ qua email này.

        Trân trọng,
        Đội ngũ hỗ trợ
    """).strip()

    html_message = textwrap.dedent(f"""
        <html>
            <body>
                <p>Xin chào <strong>{user.full_name}</strong>,</p>
                <p>Vui lòng nhấp vào liên kết dưới đây để xác thực tài khoản của bạn:</p>
                <p><a href="{activation_link}">Xác thực tài khoản</a></p>
                <p>Liên kết này sẽ hết hạn sau <strong>{settings.ACTIVATION_TOKEN_EXPIRY_HOURS} giờ</strong>.</p>
                <p>Nếu bạn không tạo tài khoản này, vui lòng bỏ qua email này.</p>
                <p>Trân trọng,<br>Đội ngũ hỗ trợ</p>
            </body>
        </html>
    """).strip()

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def verify_activation_token(token):
    from .models import User
    try:
        user = User.objects.get(activation_token=token)

        if user.activation_expiry and timezone.now() > user.activation_expiry:
            return False, "Token đã hết hạn. Vui lòng đăng ký lại."

        user.is_active = True
        user.activation_token = None
        user.activation_expiry = None
        user.save()

        return True, "Tài khoản đã được kích hoạt thành công!"
    except User.DoesNotExist:
        return False, "Token không hợp lệ."
    from django.core.mail import send_mail


logger = logging.getLogger(__name__)


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

    except SMTPException as e:
        logger.error(f"Lỗi gửi mail (SMTP): {e}")

    except Exception as e:
        logger.error(f"Lỗi không xác định khi gửi mail: {e}", exc_info=True)

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
