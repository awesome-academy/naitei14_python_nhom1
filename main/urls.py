from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    
    path('book/<int:pitch_id>/', views.book_pitch, name='book_pitch'),  # 👈 thêm dòng này

]