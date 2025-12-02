from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Booking, Pitch, PitchTimeSlot, User
from datetime import date


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(required=True, label="Họ và tên")
    phone_number = forms.CharField(required=False, label="Số điện thoại")

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'full_name',
            'phone_number',
            'password1',
            'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.full_name = self.cleaned_data["full_name"]
        user.phone_number = self.cleaned_data.get("phone_number", "")
        user.role = "User"
        if commit:
            user.save()
        return user


class DateSelectionForm(forms.Form):
    booking_date = forms.DateField(
        required=True,
        label="Chọn ngày đặt sân",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-lg',
            'min': 'today'
        })
    )

    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')
        if booking_date and booking_date < date.today():
            raise forms.ValidationError("Không thể đặt sân trong quá khứ.")
        return booking_date


class BookingForm(forms.ModelForm):
    """Form đặt sân với TimeSlot"""
    voucher_code = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mã giảm giá (nếu có)'
        }),
        label='Mã giảm giá'
    )

    class Meta:
        model = Booking
        fields = ['pitch', 'time_slot', 'booking_date', 'voucher_code', 'note']
        widgets = {
            'pitch': forms.Select(attrs={'class': 'form-control'}),
            'time_slot': forms.Select(attrs={'class': 'form-control'}),
            'booking_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ghi chú (tùy chọn)'
            }),
        }
        labels = {
            'pitch': 'Chọn sân',
            'time_slot': 'Chọn khung giờ',
            'booking_date': 'Ngày đặt',
            'note': 'Ghi chú',
        }

    def __init__(self, *args, **kwargs):
        pitch_id = kwargs.pop('pitch_id', None)
        booking_date = kwargs.pop('booking_date', None)
        super().__init__(*args, **kwargs)

        self.fields['pitch'].queryset = Pitch.objects.filter(is_available=True)

        if pitch_id:
            self.fields['pitch'].initial = pitch_id
            self.fields['pitch'].widget = forms.HiddenInput()

            all_time_slots = PitchTimeSlot.objects.filter(
                pitch_id=pitch_id,
                is_available=True
            ).select_related('time_slot')

            if booking_date:
                available_slots = []
                for pts in all_time_slots:
                    if pts.is_available_on_date(booking_date):
                        available_slots.append(pts.id)

                self.fields['time_slot'].queryset = PitchTimeSlot.objects.filter(
                    id__in=available_slots)
            else:
                self.fields['time_slot'].queryset = all_time_slots

            self.fields['time_slot'].label_from_instance = lambda obj: (
                f"{obj.time_slot.name} - {obj.get_price():,.0f}đ"
            )
        else:
            self.fields['time_slot'].queryset = PitchTimeSlot.objects.none()
            self.fields['time_slot'].widget.attrs['disabled'] = True

    def clean(self):
        cleaned_data = super().clean()
        pitch = cleaned_data.get('pitch')
        time_slot = cleaned_data.get('time_slot')
        booking_date = cleaned_data.get('booking_date')

        if pitch and time_slot and booking_date:
            if time_slot.pitch != pitch:
                raise forms.ValidationError("Khung giờ không thuộc sân này.")

            if not time_slot.is_available_on_date(booking_date):
                raise forms.ValidationError(
                    f"Khung giờ {time_slot.time_slot.name}"
                    " đã được đặt vào ngày này."
                )

        return cleaned_data
