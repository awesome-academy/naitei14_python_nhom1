from .utils import (
    send_booking_confirmation_email,
    send_booking_approved_email,
    send_booking_rejection_email,
    send_booking_cancellation_email
)
from .decorators import user_or_admin_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm, BookingForm, DateSelectionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Exists, OuterRef
from django.contrib import messages
from datetime import datetime, date
import re

from .models import Booking, Facility, Pitch, PitchTimeSlot, PitchType, Voucher, BookingStatus, Favorite, Role
from . import constants


def home(request):
    q = request.GET.get("q", "")

    facilities = Facility.objects.all()
    if q:
        facilities = facilities.filter(name__icontains=q)

    context = {
        'facilities': facilities,
        'default_facility_image': constants.DEFAULT_FACILITY_IMAGE,
    }

    if request.user.is_authenticated:
        if request.user.role == constants.ROLE_ADMIN:
            return render(request, 'host/pitch_manage.html', context)
        elif request.user.role == constants.ROLE_USER:
            return render(request, 'main/home.html', context)

    return render(request, 'main/home.html', context)


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/sign-up.html', {'form': form})


def facility_detail(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    pitches = facility.pitches.filter(is_available=True)

    context = {
        'facility': facility,
        'pitches': pitches,
        'default_facility_image': constants.DEFAULT_FACILITY_IMAGE,
        'default_pitch_image': constants.DEFAULT_PITCH_IMAGE,
        'is_user': request.user.role == constants.ROLE_USER if request.user.is_authenticated else False,
    }

    return render(request, 'user/facility_detail.html', context)


def validate_voucher_code(code):
    """
    Validate voucher code format
    Returns: (is_valid, error_message)
    """
    if not code:
        return False, "Mã giảm giá không được để trống"

    # Remove whitespace
    code = code.strip()

    # Check length
    if len(code) > constants.VOUCHER_CODE_MAX_LENGTH:
        return False, f"Mã giảm giá không được vượt quá {constants.VOUCHER_CODE_MAX_LENGTH} ký tự"

    # Check for valid characters
    if not re.match(constants.VOUCHER_CODE_PATTERN, code):
        return False, "Mã giảm giá chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới"

    return True, ""


def pitch_list(request):
    pitches = Pitch.objects.select_related('pitch_type', 'facility').all()

    search_query = request.GET.get('q', '')
    pitch_type_filter = request.GET.get('pitch_type', '')
    price_range_filter = request.GET.get('price_range', '')
    booking_date_filter = request.GET.get('booking_date', '')
    sort_by = request.GET.get('sort', 'name')

    # Filter by search query
    if search_query:
        pitches = pitches.filter(
            Q(name__icontains=search_query) |
            Q(facility__name__icontains=search_query) |
            Q(facility__address__icontains=search_query)
        )

    # Filter by pitch type
    if pitch_type_filter:
        pitches = pitches.filter(pitch_type_id=pitch_type_filter)

    # Filter by price range using constants
    if price_range_filter and price_range_filter in constants.PRICE_RANGES:
        min_price, max_price = constants.PRICE_RANGES[price_range_filter]
        if max_price == float('inf'):
            pitches = pitches.filter(base_price_per_hour__gte=min_price)
        else:
            pitches = pitches.filter(
                base_price_per_hour__gte=min_price,
                base_price_per_hour__lte=max_price
            )

    # Filter by booking date availability
    if booking_date_filter:
        try:
            booking_date = datetime.strptime(
                booking_date_filter, '%Y-%m-%d').date()

            available_time_slots = PitchTimeSlot.objects.filter(
                pitch=OuterRef('pk'), is_available=True).exclude(
                bookings__booking_date=booking_date, bookings__status__in=[
                    BookingStatus.PENDING, BookingStatus.CONFIRMED])

            pitches = pitches.annotate(
                has_available_slots=Exists(available_time_slots)
            ).filter(
                has_available_slots=True,
                is_available=True
            )

        except ValueError:
            pass

    # Sorting
    if sort_by == 'name':
        pitches = pitches.order_by('name')
    elif sort_by == '-name':
        pitches = pitches.order_by('-name')
    elif sort_by == 'price':
        pitches = pitches.order_by('base_price_per_hour')
    elif sort_by == '-price':
        pitches = pitches.order_by('-base_price_per_hour')
    else:
        pitches = pitches.order_by('name')

    has_filters = any([search_query, pitch_type_filter,
                      price_range_filter, booking_date_filter])

    pitch_types = PitchType.objects.all()

    # Pagination using constant
    paginator = Paginator(pitches, constants.ITEMS_PER_PAGE)
    page_number = request.GET.get('page')

    try:
        pitches_page = paginator.page(page_number)
    except PageNotAnInteger:
        pitches_page = paginator.page(1)
    except EmptyPage:
        pitches_page = paginator.page(paginator.num_pages)

    # Convert request.GET to dict for template
    request_get_dict = {}
    for key, value in request.GET.items():
        request_get_dict[key] = value

    context = {
        'pitches': pitches_page,
        'pitch_types': pitch_types,
        'has_filters': has_filters,
        'request_get': request_get_dict,
        'selected_booking_date': booking_date_filter,
        'default_pitch_image': constants.DEFAULT_PITCH_IMAGE,
    }

    return render(request, 'user/pitch_list.html', context)


def _apply_voucher_to_booking(booking, voucher_code, request):
    """Helper: Apply voucher to booking if valid"""
    if not voucher_code:
        return

    is_valid_format, error_message = validate_voucher_code(voucher_code)

    if not is_valid_format:
        messages.warning(
            request,
            f'{error_message}, đặt sân không áp dụng giảm giá.')
        return

    voucher_code_clean = voucher_code.strip().upper()
    try:
        voucher = Voucher.objects.get(code=voucher_code_clean)
        if voucher.is_valid():
            booking.voucher = voucher
            messages.success(
                request, f'Đã áp dụng mã giảm giá {voucher.discount_percent}%!')
        else:
            messages.warning(request, constants.ERR_VOUCHER_INVALID)
    except Voucher.DoesNotExist:
        messages.warning(request, constants.ERR_VOUCHER_NOT_FOUND)


# ============= USER BOOKING VIEWS =============

@user_or_admin_required
def user_booking_create(request, pitch_id):
    """
    Tạo booking mới

    Flow:
    1. User chọn ngày → hiển thị available time slots
    2. User chọn time slot + voucher (optional) → tạo booking
    3. Gửi email xác nhận → redirect to booking detail
    """
    pitch = get_object_or_404(Pitch, id=pitch_id, is_available=True)

    # Get booking date from GET or POST
    booking_date_str = request.GET.get(
        'date') or request.POST.get('booking_date')
    booking_date = None

    if booking_date_str:
        try:
            booking_date = datetime.strptime(
                booking_date_str, '%Y-%m-%d').date()
        except ValueError:
            booking_date = None

    if request.method == 'POST':
        form = BookingForm(
            request.POST,
            pitch_id=pitch_id,
            booking_date=booking_date
        )

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.pitch = pitch

            # Apply voucher if provided
            voucher_code = form.cleaned_data.get('voucher_code')
            _apply_voucher_to_booking(booking, voucher_code, request)

            # Save booking (auto-calculate duration & price in model)
            booking.save()

            # Send confirmation email
            send_booking_confirmation_email(booking)

            messages.success(request, constants.MSG_BOOKING_CREATED)
            return redirect('user_booking_detail', booking_id=booking.id)
    else:
        form = BookingForm(pitch_id=pitch_id, booking_date=booking_date)

    # Load available time slots for selected date
    available_time_slots = []
    if booking_date:
        all_time_slots = PitchTimeSlot.objects.filter(
            pitch=pitch,
            is_available=True
        ).select_related('time_slot').order_by('time_slot__start_time')

        for pts in all_time_slots:
            available_time_slots.append({
                'id': pts.id,
                'name': pts.time_slot.name,
                'start_time': pts.time_slot.start_time,
                'end_time': pts.time_slot.end_time,
                'duration': pts.time_slot.duration_hours(),
                'price': pts.get_price(),
                'is_available': pts.is_available_on_date(booking_date)
            })

    context = {
        'form': form,
        'pitch': pitch,
        'booking_date': booking_date,
        'available_time_slots': available_time_slots,
        'today': date.today().isoformat(),
        'default_pitch_image': constants.DEFAULT_PITCH_IMAGE,
    }
    return render(request, 'user/booking_create.html', context)


@user_or_admin_required
def user_booking_list(request):
    """Danh sách booking của user (hoặc tất cả nếu là admin)"""
    if request.user.role == Role.ADMIN:
        bookings = Booking.objects.all()
    else:
        bookings = Booking.objects.filter(user=request.user)

    bookings = bookings.select_related(
        'pitch', 'time_slot__time_slot', 'voucher'
    ).order_by('-booking_date', '-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Pagination
    paginator = Paginator(bookings, constants.BOOKINGS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'booking_statuses': BookingStatus.choices,
        'is_admin': request.user.role == Role.ADMIN,
    }
    return render(request, 'user/booking_list.html', context)


@user_or_admin_required
def user_booking_detail(request, booking_id):
    """Chi tiết booking"""
    if request.user.role == Role.ADMIN:
        booking = get_object_or_404(Booking, id=booking_id)
    else:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    context = {
        'booking': booking,
        'is_admin': request.user.role == Role.ADMIN,
        'can_cancel': booking.status == BookingStatus.PENDING,
        'can_approve': (
            request.user.role == Role.ADMIN
            and booking.status == BookingStatus.PENDING),
    }
    return render(request, 'user/booking_detail.html', context)


@user_or_admin_required
def user_booking_cancel(request, booking_id):
    """Hủy booking (chỉ với status PENDING)"""
    if request.user.role == Role.ADMIN:
        booking = get_object_or_404(Booking, id=booking_id)
    else:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != BookingStatus.PENDING:
        messages.error(request, constants.ERR_BOOKING_ONLY_CANCEL_PENDING)
        return redirect('user_booking_detail', booking_id=booking_id)

    if request.method == 'POST':

        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=['status'])

        # Send cancellation email
        send_booking_cancellation_email(booking)

        messages.success(request, constants.MSG_BOOKING_CANCELLED)
        return redirect('user_booking_list')

    context = {
        'booking': booking,
        'is_admin': request.user.role == Role.ADMIN,
    }
    return render(request, 'user/booking_cancel.html', context)


# ============= ADMIN BOOKING VIEWS =============

@login_required
def admin_booking_approve(request, booking_id):
    """Admin duyệt booking (PENDING → CONFIRMED)"""
    if request.user.role != Role.ADMIN:
        messages.error(request, constants.ERR_NO_PERMISSION)
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status != BookingStatus.PENDING:
        messages.error(request, constants.ERR_BOOKING_ONLY_APPROVE_PENDING)
        return redirect('user_booking_detail', booking_id=booking_id)

    booking.status = BookingStatus.CONFIRMED
    booking.save()

    # Send approval email to user
    send_booking_approved_email(booking)

    messages.success(
        request,
        constants.MSG_BOOKING_APPROVED.format(
            booking_id=booking.id))
    return redirect('user_booking_list')


@login_required
def admin_booking_reject(request, booking_id):
    """Admin từ chối booking (PENDING → REJECTED)"""
    if request.user.role != Role.ADMIN:
        messages.error(request, constants.ERR_NO_PERMISSION)
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status != BookingStatus.PENDING:
        messages.error(request, constants.ERR_BOOKING_ONLY_APPROVE_PENDING)
        return redirect('user_booking_detail', booking_id=booking_id)

    # Get rejection reason from POST if available
    reason = request.POST.get('reason', '') if request.method == 'POST' else ''

    booking.status = BookingStatus.REJECTED
    booking.save()

    # Send rejection email to user
    send_booking_rejection_email(booking, reason=reason)

    messages.warning(
        request,
        constants.MSG_BOOKING_REJECTED.format(
            booking_id=booking.id))
    return redirect('user_booking_list')


def get_available_time_slots_ajax(request, pitch_id):
    """AJAX: Lấy available time slots cho ngày cụ thể"""
    pitch = get_object_or_404(Pitch, id=pitch_id)
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': 'Missing date parameter'}, status=400)

    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    all_time_slots = PitchTimeSlot.objects.filter(
        pitch=pitch,
        is_available=True
    ).select_related('time_slot').order_by('time_slot__start_time')

    slots_data = []
    for pts in all_time_slots:
        slots_data.append({
            'id': pts.id,
            'name': pts.time_slot.name,
            'start_time': pts.time_slot.start_time.strftime('%H:%M'),
            'end_time': pts.time_slot.end_time.strftime('%H:%M'),
            'duration': float(pts.time_slot.duration_hours()),
            'price': float(pts.get_price()),
            'is_available': pts.is_available_on_date(booking_date)
        })

    return JsonResponse({'date': date_str, 'slots': slots_data})


def check_voucher_ajax(request):
    """AJAX: Kiểm tra mã giảm giá"""
    code = request.GET.get('code', '')

    if not code:
        return JsonResponse(
            {'valid': False, 'message': 'Vui lòng nhập mã giảm giá'})

    is_valid_format, error_message = validate_voucher_code(code)

    if not is_valid_format:
        return JsonResponse({'valid': False, 'message': error_message})

    code_clean = code.strip().upper()

    try:
        voucher = Voucher.objects.get(code=code_clean)
        if voucher.is_valid():
            return JsonResponse({
                'valid': True,
                'message': f'Mã giảm {voucher.discount_percent}% có hiệu lực!',
                'discount_percent': voucher.discount_percent
            })
        else:
            return JsonResponse(
                {'valid': False, 'message': 'Mã giảm giá đã hết hạn'})
    except Voucher.DoesNotExist:
        return JsonResponse(
            {'valid': False, 'message': 'Mã giảm giá không tồn tại'})


@user_or_admin_required
def user_toggle_favorite(request, pitch_id):
    """Toggle yêu thích sân"""
    pitch = get_object_or_404(Pitch, id=pitch_id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        pitch=pitch
    )

    if not created:
        favorite.delete()
        messages.info(request, f'Đã bỏ yêu thích {pitch.name}.')
        is_favorited = False
    else:
        messages.success(request, f'Đã thêm {pitch.name} vào yêu thích.')
        is_favorited = True

    # Return JSON for AJAX or redirect for normal request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorited': is_favorited})

    return redirect('facility_detail', facility_id=pitch.facility.id)


@user_or_admin_required
def user_favorites(request):
    """Danh sách sân yêu thích"""
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('pitch', 'pitch__facility')

    context = {
        'favorites': favorites,
        'default_pitch_image': constants.DEFAULT_PITCH_IMAGE,
    }
    return render(request, 'user/favorites.html', context)
