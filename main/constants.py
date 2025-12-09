DEFAULT_PITCH_IMAGE = (
    "https://manager.datsan247.com/assets/images/"
    "banner-client-placeholder.jpg"
)

DEFAULT_FACILITY_IMAGE = (
    "https://manager.datsan247.com/assets/images/"
    "banner-client-placeholder.jpg"
)

BOOKING_STATUS_PENDING = 'Pending'
BOOKING_STATUS_CONFIRMED = 'Confirmed'
BOOKING_STATUS_CANCELLED = 'Cancelled'
BOOKING_STATUS_COMPLETED = 'Completed'


ITEMS_PER_PAGE = 6
MAX_PAGINATION_LINKS = 5
BOOKINGS_PER_PAGE = 10

ADMIN_LIST_PER_PAGE = 20
ADMIN_INLINE_EXTRA = 1

PRICE_RANGES = {
    '0-100000': (0, 100000),
    '100000-200000': (100000, 200000),
    '200000-300000': (200000, 300000),
    '300000': (300000, float('inf')),
}

VOUCHER_CODE_MAX_LENGTH = 50
VOUCHER_CODE_PATTERN = r'^[A-Za-z0-9\-_]+$'

MIN_BOOKING_ADVANCE_DAYS = 0
MAX_BOOKING_ADVANCE_DAYS = 14

ROLE_ADMIN = "Admin"
ROLE_USER = "User"

DATE_HIERARCHY_BOOKING = 'booking_date'

READONLY_TIMESTAMP_FIELDS = ('created_at', 'updated_at')
READONLY_ACTIVATION_FIELDS = ('activation_token', 'activation_expiry')

BOOKING_READONLY_FIELDS = (
    'created_at',
    'updated_at',
    'duration_hours',
    'final_price',
    'time_slot')

VOUCHER_READONLY_FIELDS = ('created_at', 'used_count')

EMAIL_SUBJECT_BOOKING_CONFIRMATION = "Xác nhận đặt sân #{booking_id}"
EMAIL_SUBJECT_BOOKING_REJECTION = "Từ chối đặt sân #{booking_id}"
EMAIL_SUBJECT_BOOKING_CANCELLATION = "Hủy đặt sân #{booking_id}"
EMAIL_SUBJECT_BOOKING_APPROVED = "Đã duyệt đặt sân #{booking_id}"


EMAIL_TEMPLATE_BOOKING_CONFIRMATION = """
Xin chào {user_name},

Bạn đã đặt sân thành công!

Thông tin đặt sân:
- Sân: {pitch_name}
- Ngày: {booking_date}
- Khung giờ: {time_slot_name} ({start_time} - {end_time})
- Tổng tiền: {final_price}đ

Trạng thái: Đang chờ xác nhận

Vui lòng đợi admin xác nhận đặt sân của bạn.

Trân trọng,
Hệ thống đặt sân bóng
"""

EMAIL_TEMPLATE_BOOKING_APPROVED = """
Xin chào {user_name},

Đặt sân của bạn đã được duyệt!

Thông tin đặt sân:
- Sân: {pitch_name}
- Ngày: {booking_date}
- Khung giờ: {time_slot_name} ({start_time} - {end_time})
- Tổng tiền: {final_price}đ

Vui lòng đến sân đúng giờ và thanh toán khi đến.

Trân trọng,
Hệ thống đặt sân bóng
"""

EMAIL_TEMPLATE_BOOKING_REJECTION = """
Xin chào {user_name},

Rất tiếc, yêu cầu đặt sân của bạn đã bị từ chối.

Thông tin đặt sân:
- Sân: {pitch_name}
- Ngày: {booking_date}
- Khung giờ: {time_slot_name} ({start_time} - {end_time})

Lý do: {reason}

Vui lòng chọn khung giờ khác hoặc liên hệ với chúng tôi để được hỗ trợ.

Trân trọng,
Hệ thống đặt sân bóng
"""

EMAIL_TEMPLATE_BOOKING_CANCELLATION = """
Xin chào {user_name},

Đặt sân của bạn đã bị hủy.

Thông tin đặt sân:
- Sân: {pitch_name}
- Ngày: {booking_date}
- Khung giờ: {time_slot_name} ({start_time} - {end_time})

Nếu bạn muốn đặt lại, vui lòng truy cập hệ thống.

Trân trọng,
Hệ thống đặt sân bóng
"""


MSG_BOOKING_CREATED = "Đặt sân thành công! Vui lòng chờ xác nhận."
MSG_BOOKING_CANCELLED = "Đã hủy đặt sân."
MSG_BOOKING_APPROVED = "Đã duyệt booking #{booking_id}."
MSG_BOOKING_REJECTED = "Đã từ chối booking #{booking_id}."

MSG_FAVORITE_ADDED = "Đã thêm {pitch_name} vào yêu thích."
MSG_FAVORITE_REMOVED = "Đã bỏ yêu thích {pitch_name}."

MSG_REVIEW_CREATED = "Cảm ơn bạn đã đánh giá!"


ERR_BOOKING_DATE_PAST = "Không thể đặt lịch trong quá khứ."
ERR_BOOKING_SLOT_TAKEN = "Khung giờ {time_slot_name} đã được đặt vào ngày này."
ERR_BOOKING_SLOT_MISMATCH = "Khung giờ không thuộc về sân này."
ERR_BOOKING_ONLY_CANCEL_PENDING = "Chỉ có thể hủy đặt sân đang chờ xác nhận."
ERR_BOOKING_ONLY_APPROVE_PENDING = "Chỉ có thể duyệt booking đang chờ."

ERR_VOUCHER_INVALID = "Mã giảm giá không hợp lệ hoặc đã hết hạn."
ERR_VOUCHER_NOT_FOUND = "Mã giảm giá không tồn tại."

ERR_REVIEW_ONLY_AFTER_BOOKING = "Bạn chỉ có thể đánh giá sân đã đặt."
ERR_REVIEW_ALREADY_EXISTS = "Bạn đã đánh giá sân này rồi."


INFO_SELECT_DATE_FIRST = "Vui lòng chọn ngày để xem khung giờ có sẵn."
INFO_NO_BOOKINGS = "Bạn chưa có lịch đặt sân nào."
INFO_NO_FAVORITES = "Bạn chưa có sân yêu thích nào."
INFO_NO_PITCHES_FOUND = "Không tìm thấy sân bóng nào."


WARN_LOGIN_REQUIRED = "Vui lòng đăng nhập để sử dụng chức năng này."
WARN_PERMISSION_DENIED = "Bạn không có quyền truy cập chức năng này."


URL_HOME = "home"
URL_LOGIN = "login"
URL_REGISTER = "register"
URL_LOGOUT = "logout"

URL_PITCH_LIST = "user_pitch_list"
URL_PITCH_DETAIL = "user_pitch_detail"

URL_BOOKING_LIST = "user_booking_list"
URL_BOOKING_CREATE = "user_booking_create"
URL_BOOKING_DETAIL = "user_booking_detail"
URL_BOOKING_CANCEL = "user_booking_cancel"

URL_FAVORITES = "user_favorites"
URL_TOGGLE_FAVORITE = "user_toggle_favorite"

URL_ADMIN_DASHBOARD = "admin_dashboard"
URL_ADMIN_BOOKING_APPROVE = "admin_booking_approve"
URL_ADMIN_BOOKING_REJECT = "admin_booking_reject"

BOOKING_STATUS_BADGE_COLORS = {
    'Pending': 'bg-warning',
    'Confirmed': 'bg-success',
    'Cancelled': 'bg-secondary',
    'Rejected': 'bg-danger',
}


ICON_HOME = "fas fa-home"
ICON_PITCH = "fas fa-futbol"
ICON_BOOKING = "fas fa-calendar-check"
ICON_FAVORITE = "fas fa-heart"
ICON_USER = "fas fa-user"
ICON_ADMIN = "fas fa-user-shield"
ICON_DASHBOARD = "fas fa-tachometer-alt"
ICON_APPROVE = "fas fa-check"
ICON_REJECT = "fas fa-times"
ICON_EDIT = "fas fa-edit"
ICON_DELETE = "fas fa-trash"
ICON_VIEW = "fas fa-eye"
ICON_SEARCH = "fas fa-search"
