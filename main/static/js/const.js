// Global config injected from backend (HTML template)
export const APP_CONFIG = window.appConfig || {};

// Không hardcode locale
export const LOCALE =
    APP_CONFIG.locale ||
    document.documentElement.lang ||
    navigator.language;

// Không hardcode query param name
export const QUERY_KEYS = {
    bookingDate: APP_CONFIG.bookingDateKey || 'date'
};


// Text constants
export const TEXT = {
    TIME_SLOT_REQUIRED_MSG: 'Vui lòng chọn khung giờ.',
    MSG_ENTER_VOUCHER: 'Vui lòng nhập mã voucher.',
    MSG_VOUCHER_CHECKING: 'Đang kiểm tra...',
    MSG_VOUCHER_VALID: 'Voucher hợp lệ!',
    MSG_VOUCHER_INVALID: 'Voucher không hợp lệ!',
    MSG_VOUCHER_ERROR: 'Có lỗi xảy ra, vui lòng thử lại.'
};

export const URL_CONFIG = {
    queryPrefix: (APP_CONFIG.queryPrefix || '?')
};
