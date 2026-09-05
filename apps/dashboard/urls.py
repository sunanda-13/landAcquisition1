from django.urls import path
from .views import DashboardView, DashboardChartsApiView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/charts/', DashboardChartsApiView.as_view(), name='dashboard_charts_api'),
]
