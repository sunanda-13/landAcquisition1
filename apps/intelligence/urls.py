from django.urls import path
from .views import api_simulate_case

urlpatterns = [
    path('simulate/<int:pk>/', api_simulate_case, name='api_simulate_case'),
]
