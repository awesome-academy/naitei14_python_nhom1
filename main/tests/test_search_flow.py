from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from datetime import date, time, timedelta
from main.models import Facility, Pitch, PitchType, PitchTimeSlot, TimeSlot, Booking, BookingStatus, User
from main import constants


class PitchSearchFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('pitch_list')

        # Facilities
        self.downtown = Facility.objects.create(
            name="Downtown Sports", address="Downtown")
        self.uptown = Facility.objects.create(
            name="Uptown Arena", address="Uptown")

        # Pitch Types
        self.type_5 = PitchType.objects.create(name="5vs5")
        self.type_7 = PitchType.objects.create(name="7vs7")

        # Pitches
        self.p1 = Pitch.objects.create(
            name="Alpha Pitch",
            facility=self.downtown,
            pitch_type=self.type_5,
            base_price_per_hour=Decimal('100000'),
            is_available=True
        )
        self.p2 = Pitch.objects.create(
            name="Beta Pitch",
            facility=self.downtown,
            pitch_type=self.type_7,
            base_price_per_hour=Decimal('200000'),
            is_available=True
        )
        self.p3 = Pitch.objects.create(
            name="Gamma Pitch",
            facility=self.uptown,
            pitch_type=self.type_5,
            base_price_per_hour=Decimal('150000'),
            is_available=True
        )
        self.p4 = Pitch.objects.create(
            name="Delta Pitch",
            facility=self.uptown,
            pitch_type=self.type_7,
            base_price_per_hour=Decimal('300000'),
            is_available=True
        )
        self.p5_unavailable = Pitch.objects.create(
            name="Unavailable Pitch",
            facility=self.downtown,
            pitch_type=self.type_5,
            base_price_per_hour=Decimal('100000'),
            is_available=False
        )

    def test_search_by_keyword(self):
        """Test search by keyword (name, facility name, address)"""
        # Search by pitch name
        response = self.client.get(self.url, {'q': 'Alpha'})
        self.assertIn(self.p1, response.context['pitches'])
        self.assertNotIn(self.p2, response.context['pitches'])

        # Search by facility name
        response = self.client.get(self.url, {'q': 'Uptown'})
        self.assertIn(self.p3, response.context['pitches'])
        self.assertIn(self.p4, response.context['pitches'])
        self.assertNotIn(self.p1, response.context['pitches'])

        # Case insensitive
        response = self.client.get(self.url, {'q': 'alpha'})
        self.assertIn(self.p1, response.context['pitches'])

    def test_filter_by_pitch_type(self):
        """Test filter by pitch type"""
        response = self.client.get(self.url, {'pitch_type': self.type_5.id})
        pitches = response.context['pitches']
        self.assertIn(self.p1, pitches)
        self.assertIn(self.p3, pitches)
        self.assertNotIn(self.p2, pitches)
        self.assertNotIn(self.p4, pitches)

    def test_filter_by_price_range(self):
        """Test filter by price range"""
        # 0-100000 (Inclusive)
        response = self.client.get(self.url, {'price_range': '0-100000'})
        pitches = response.context['pitches']
        self.assertIn(self.p1, pitches)
        self.assertNotIn(self.p2, pitches)  # 200k
        self.assertNotIn(self.p3, pitches)  # 150k

        # 200000-300000
        response = self.client.get(self.url, {'price_range': '200000-300000'})
        pitches = response.context['pitches']
        self.assertIn(self.p2, pitches)  # 200k
        self.assertIn(self.p4, pitches)  # 300k
        self.assertNotIn(self.p1, pitches)

    def test_sort_by_price(self):
        """Test sorting by price"""
        # Ascending
        response = self.client.get(self.url, {'sort': 'price'})
        pitches = list(response.context['pitches'])
        # Expected order: 100k, 100k, 150k, 200k, 300k
        prices = [p.base_price_per_hour for p in pitches]
        self.assertEqual(prices, sorted(prices))

        # Descending
        response = self.client.get(self.url, {'sort': '-price'})
        pitches = list(response.context['pitches'])
        prices = [p.base_price_per_hour for p in pitches]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_sort_by_name(self):
        """Test sorting by name"""
        response = self.client.get(self.url, {'sort': 'name'})
        pitches = list(response.context['pitches'])
        names = [p.name for p in pitches]
        self.assertEqual(names, sorted(names))

    def test_combine_search_filter_sort(self):
        """Test combining search, filter and sort"""
        # Search "Downtown", Type 5vs5, Sort -price
        response = self.client.get(self.url, {
            'q': 'Downtown',
            'pitch_type': self.type_5.id,
            'sort': '-price'
        })
        pitches = list(response.context['pitches'])

        # Should match P1 (100k) and P5 (100k)
        self.assertIn(self.p1, pitches)
        self.assertIn(self.p5_unavailable, pitches)
        self.assertNotIn(self.p2, pitches)  # Wrong type
        self.assertNotIn(self.p3, pitches)  # Wrong facility

    def test_exclude_unavailable_pitches_with_date(self):
        """Test that unavailable pitches are excluded when filtering by date"""
        booking_date = date.today() + timedelta(days=1)

        # Need to set up TimeSlots and PitchTimeSlots for availability check
        ts = TimeSlot.objects.create(
            name="7h-9h",
            start_time=time(
                7,
                0),
            end_time=time(
                9,
                0))

        # P1 has slot
        PitchTimeSlot.objects.create(
            pitch=self.p1, time_slot=ts, is_available=True)
        # P5 has slot but pitch is unavailable
        PitchTimeSlot.objects.create(
            pitch=self.p5_unavailable,
            time_slot=ts,
            is_available=True)

        response = self.client.get(self.url, {
            'booking_date': booking_date.strftime('%Y-%m-%d')
        })

        pitches = response.context['pitches']
        self.assertIn(self.p1, pitches)
        self.assertNotIn(self.p5_unavailable, pitches)

    def test_filter_by_date_excludes_booked_pitches(self):
        """Test that pitches with no available slots are excluded"""
        booking_date = date.today() + timedelta(days=1)
        ts = TimeSlot.objects.create(
            name="7h-9h",
            start_time=time(
                7,
                0),
            end_time=time(
                9,
                0))

        # P1 has slot but it is BOOKED
        pts1 = PitchTimeSlot.objects.create(
            pitch=self.p1, time_slot=ts, is_available=True)
        Booking.objects.create(
            user=User.objects.create_user(username='u1'),
            pitch=self.p1,
            time_slot=pts1,
            booking_date=booking_date,
            status=BookingStatus.CONFIRMED
        )

        # P2 has slot and is FREE
        pts2 = PitchTimeSlot.objects.create(
            pitch=self.p2, time_slot=ts, is_available=True)

        response = self.client.get(self.url, {
            'booking_date': booking_date.strftime('%Y-%m-%d')
        })

        pitches = response.context['pitches']
        self.assertNotIn(self.p1, pitches)  # No slots left
        self.assertIn(self.p2, pitches)
