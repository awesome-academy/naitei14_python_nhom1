import { LOCALE, QUERY_KEYS, TEXT } from './const.js';

// ============= DATE CHANGE HANDLER =============
const bookingDateInput = document.getElementById('bookingDate');
if (bookingDateInput) {
    bookingDateInput.addEventListener('change', function () {
        const selectedDate = this.value;

        if (selectedDate) {
            const key = QUERY_KEYS.bookingDate;
            window.location.href = `?${key}=${encodeURIComponent(selectedDate)}`;
        }
    });
}

// ============= TIME SLOT SELECT =============
function selectTimeSlot(card) {
    if (!card || card.dataset.available !== 'true') return;

    document.querySelectorAll('.time-slot-card').forEach(c => {
        c.classList.remove('selected');
    });

    card.classList.add('selected');

    const { slotId, slotName, slotTime, slotPrice } = card.dataset;

    document.getElementById('selectedTimeSlot').value = slotId;
    document.getElementById('selectedSlotName').textContent = slotName;
    document.getElementById('selectedSlotTime').textContent = slotTime;
    document.getElementById('selectedSlotPrice').textContent =
        Number(slotPrice).toLocaleString(LOCALE);

    document.getElementById('selectedSlotInfo').classList.remove('d-none');

    // Enable submit button
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.disabled = false;
    }
}

document.querySelectorAll('.time-slot-card').forEach(card => {
    card.addEventListener('click', () => selectTimeSlot(card));
});


// ============= VOUCHER CHECK =============
async function checkVoucher() {
    const code = document.getElementById('voucherCode').value.trim();
    const messageDiv = document.getElementById('voucherMessage');

    if (!code) {
        messageDiv.textContent = TEXT.MSG_ENTER_VOUCHER;
        return;
    }

    messageDiv.textContent = TEXT.MSG_VOUCHER_CHECKING;

    try {
        const url = `${window.checkVoucherUrl}?code=${encodeURIComponent(code)}`;
        const res = await fetch(url);

        if (!res.ok) {
            const error = new Error('Voucher HTTP error');
            error.name = 'VoucherCheckError';
            error.context = { status: res.status };
            throw error;
        }

        const data = await res.json();

        messageDiv.textContent = data.valid
            ? TEXT.MSG_VOUCHER_VALID
            : TEXT.MSG_VOUCHER_INVALID;

    } catch (err) {
        messageDiv.textContent = TEXT.MSG_VOUCHER_ERROR;

        // 3. Log error
        console.error({
            level: 'error',
            type: err.name,
            message: err.message,
            context: err.context || null,
            time: new Date().toISOString()
        });

        return;
    }
}

const voucherBtn = document.getElementById('checkVoucherBtn');
if (voucherBtn) {
    voucherBtn.addEventListener('click', checkVoucher);
}

// ============= FORM VALIDATION =============
const bookingForm = document.getElementById('bookingForm');
if (bookingForm) {
    bookingForm.addEventListener('submit', function (e) {
        const timeSlot = document.getElementById('selectedTimeSlot').value;

        if (!timeSlot) {
            e.preventDefault();
            const msg = document.getElementById('formMessage');
            if (msg) {
                msg.textContent = TEXT.TIME_SLOT_REQUIRED_MSG;
                msg.classList.remove('d-none');
            }
        }
    });
}
