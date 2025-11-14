from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout

from .models import Pitch
# Create your views here.
def home(request):
    pitches = Pitch.objects.all()  # 👈 lấy danh sách sân
    if request.user.is_authenticated:
        if request.user.role == "Admin":
            return render(request, 'host/pitch_manage.html', {'pitches': pitches})
        elif request.user.role == "User":
            return render(request, 'user/pitch_list.html', {'pitches': pitches})
    return render(request, 'user/pitch_list.html', {'pitches': pitches})

def sign_up(request):
        if request.method == 'POST':
                form = SignUpForm(request.POST)
                if form.is_valid():
                        user = form.save()
                        login(request, user)
                        return redirect('/home')
        else:
                form = SignUpForm()
        return render(request, 'registration/sign-up.html', {'form': form})

@login_required(login_url='login')
def book_pitch(request, pitch_id):
    # Chặn người không phải User (ví dụ Admin hoặc Guest)
    if request.user.role != "User":
        return HttpResponseForbidden("Bạn không có quyền đặt sân!")

    pitch = get_object_or_404(Pitch, id=pitch_id)
    return render(request, 'user/bookPitch.html', {'pitch': pitch})