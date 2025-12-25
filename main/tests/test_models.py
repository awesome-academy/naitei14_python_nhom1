from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, time, timedelta, datetime
from decimal import Decimal
from main.models import (
    User, Facility, Pitch, PitchType, TimeSlot, PitchTimeSlot,
    Voucher, Booking, BookingStatus, Role
)


class TimeSlotModelTest(TestCase):
    def test_duration_hours_full_hour(self):
        """Test duration calculation for full hours"""
        slot = TimeSlot(
            name="7h-9h",
            start_time=time(7, 0),
            end_time=time(9, 0)
        )
        self.assertEqual(slot.duration_hours(), Decimal('2.00'))

    def test_duration_hours_half_hour(self):
        """Test duration calculation for half hours"""
        slot = TimeSlot(
            name="7h-8h30",
            start_time=time(7, 0),
            end_time=time(8, 30)
        )
        self.assertEqual(slot.duration_hours(), Decimal('1.50'))

    def test_clean_invalid_time(self):
        """Test validation when start_time >= end_time"""
        slot = TimeSlot(
            name="Invalid",
            start_time=time(9, 0),
            end_time=time(8, 0)
        )
        with self.assertRaises(ValidationError):
            slot.clean()

        slot_equal = TimeSlot(
            name="Equal",
            start_time=time(9, 0),
            end_time=time(9, 0)
        )
        with self.assertRaises(ValidationError):
            slot_equal.clean()


class VoucherModelTest(TestCase):
    def setUp(self):
        self.voucher = Voucher.objects.create(
            code="TEST10",
            discount_percent=10,
            is_active=True
        )

    def test_is_valid_active(self):
        """Test valid voucher"""
        self.assertTrue(self.voucher.is_valid())

    def test_is_valid_expired(self):
        """Test expired voucher"""
        self.voucher.end_date = date.today() - timedelta(days=1)
        self.voucher.save()
        self.assertFalse(self.voucher.is_valid())

    def test_is_valid_not_started(self):
        """Test voucher not yet started"""
        self.voucher.start_date = date.today() + timedelta(days=1)
        self.voucher.save()
        self.assertFalse(self.voucher.is_valid())

    def test_is_valid_inactive(self):
        """Test inactive voucher"""
        self.voucher.is_active = False
        self.voucher.save()
        self.assertFalse(self.voucher.is_valid())

    def test_is_valid_usage_limit_exceeded(self):
        """Test usage limit exceeded"""
        self.voucher.usage_limit = 1
        self.voucher.used_count = 1
        self.voucher.save()
        self.assertFalse(self.voucher.is_valid())

    def test_clean_invalid_date_range(self):
        """Test validation when start_date > end_date"""
        self.voucher.start_date = date.today()
        self.voucher.end_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.voucher.clean()


class PitchTimeSlotModelTest(TestCase):
    def setUp(self):
        self.facility = Facility.objects.create(
            name="Test Facility", address="Address")
        self.pitch_type = PitchType.objects.create(name="5vs5")
        self.pitch = Pitch.objects.create(
            facility=self.facility,
            name="Pitch 1",
            pitch_type=self.pitch_type,
            base_price_per_hour=Decimal('100000')
        )
        self.time_slot = TimeSlot.objects.create(
            name="7h-9h",
            start_time=time(7, 0),
            end_time=time(9, 0)
        )
        self.pitch_time_slot = PitchTimeSlot.objects.create(
            pitch=self.pitch,
            time_slot=self.time_slot
        )
        self.user = User.objects.create_user(
            username="testuser", password="password")

    def test_get_price(self):
        """Test price calculation based on pitch price and duration"""
        # 100,000 * 2 hours = 200,000
        self.assertEqual(
            self.pitch_time_slot.get_price(),
            Decimal('200000.00'))

    def test_is_available_on_date_no_booking(self):
        """Test availability when no booking exists"""
        booking_date = date.today() + timedelta(days=1)
        self.assertTrue(
            self.pitch_time_slot.is_available_on_date(booking_date))

    def test_is_available_on_date_with_confirmed_booking(self):
        """Test unavailable when confirmed booking exists"""
        booking_date = date.today() + timedelta(days=1)
        Booking.objects.create(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=booking_date,
            status=BookingStatus.CONFIRMED
        )
        self.assertFalse(
            self.pitch_time_slot.is_available_on_date(booking_date))

    def test_is_available_on_date_with_pending_booking(self):
        """Test unavailable when pending booking exists"""
        booking_date = date.today() + timedelta(days=1)
        Booking.objects.create(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=booking_date,
            status=BookingStatus.PENDING
        )
        self.assertFalse(
            self.pitch_time_slot.is_available_on_date(booking_date))

    def test_is_available_on_date_with_cancelled_booking(self):
        """Test available when booking is cancelled"""
        booking_date = date.today() + timedelta(days=1)
        Booking.objects.create(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=booking_date,
            status=BookingStatus.CANCELLED
        )
        self.assertTrue(
            self.pitch_time_slot.is_available_on_date(booking_date))

    def test_is_available_on_date_with_rejected_booking(self):
        """Test available when booking is rejected"""
        booking_date = date.today() + timedelta(days=1)
        Booking.objects.create(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=booking_date,
            status=BookingStatus.REJECTED
        )
        self.assertTrue(
            self.pitch_time_slot.is_available_on_date(booking_date))


class BookingModelTest(TestCase):
    def setUp(self):
        self.facility = Facility.objects.create(
            name="Test Facility", address="Address")
        self.pitch_type = PitchType.objects.create(name="5vs5")
        self.pitch = Pitch.objects.create(
            facility=self.facility,
            name="Pitch 1",
            pitch_type=self.pitch_type,
            base_price_per_hour=Decimal('100000')
        )
        self.time_slot = TimeSlot.objects.create(
            name="7h-9h",
            start_time=time(7, 0),
            end_time=time(9, 0)
        )
        self.pitch_time_slot = PitchTimeSlot.objects.create(
            pitch=self.pitch,
            time_slot=self.time_slot
        )
        self.user = User.objects.create_user(
            username="testuser", password="password")
        self.booking_date = date.today() + timedelta(days=1)

    def test_save_calculates_duration_and_price(self):
        """Test that save() automatically calculates duration and final_price"""
        booking = Booking(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=self.booking_date
        )
        booking.save()

        self.assertEqual(booking.duration_hours, Decimal('2.00'))
        self.assertEqual(booking.final_price, Decimal('200000.00'))

    def test_save_with_voucher(self):
        """Test final price calculation with voucher"""
        voucher = Voucher.objects.create(
            code="TEST10",
            discount_percent=10,
            is_active=True
        )
        booking = Booking(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=self.booking_date,
            voucher=voucher
        )
        booking.save()

        # 200,000 - 10% = 180,000
        self.assertEqual(booking.final_price, Decimal('180000.00'))

    def test_save_increments_voucher_usage(self):
        """Test that saving a new booking increments voucher used_count"""
        voucher = Voucher.objects.create(
            code="TEST10",
            discount_percent=10,
            is_active=True,
            used_count=0
        )
        booking = Booking(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=self.booking_date,
            voucher=voucher
        )
        booking.save()

        voucher.refresh_from_db()
        self.assertEqual(voucher.used_count, 1)

    def test_clean_past_date(self):
        """Test validation for booking in the past"""
        past_date = date.today() - timedelta(days=1)
        booking = Booking(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=past_date,
            status=BookingStatus.PENDING
        )
        with self.assertRaises(ValidationError) as cm:
            booking.clean()
        self.assertIn('booking_date', cm.exception.message_dict)

    def test_clean_time_slot_mismatch(self):
        """Test validation when time_slot does not belong to pitch"""
        other_pitch = Pitch.objects.create(
            facility=self.facility,
            name="Pitch 2",
            pitch_type=self.pitch_type,
            base_price_per_hour=Decimal('100000')
        )
        # pitch_time_slot belongs to self.pitch, but we try to book other_pitch
        booking = Booking(
            user=self.user,
            pitch=other_pitch,
            time_slot=self.pitch_time_slot,
            booking_date=self.booking_date
        )
        with self.assertRaises(ValidationError) as cm:
            booking.clean()
        self.assertIn('time_slot', cm.exception.message_dict)

    def test_clean_duplicate_booking(self):
        """Test validation when booking an already booked slot"""
        # Create first booking
        Booking.objects.create(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=self.booking_date,
            status=BookingStatus.CONFIRMED
        )

        # Try to create second booking for same slot
        booking2 = Booking(
            user=self.user,
            pitch=self.pitch,
            time_slot=self.pitch_time_slot,
            booking_date=self.booking_date,
            status=BookingStatus.PENDING
        )

        with self.assertRaises(ValidationError) as cm:
            booking2.clean()
        self.assertIn('time_slot', cm.exception.message_dict)
