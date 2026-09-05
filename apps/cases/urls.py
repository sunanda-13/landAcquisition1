from django.urls import path
from .views import (
    CaseListView,
    CaseDetailView,
    CaseCreateView,
    CaseUpdateView,
    CaseDeleteView,
    RecalculateRiskView
)

urlpatterns = [
    path('', CaseListView.as_view(), name='case_list'),
    path('create/', CaseCreateView.as_view(), name='case_create'),
    path('<int:pk>/', CaseDetailView.as_view(), name='case_detail'),
    path('<int:pk>/edit/', CaseUpdateView.as_view(), name='case_update'),
    path('<int:pk>/delete/', CaseDeleteView.as_view(), name='case_delete'),
    path('<int:pk>/recalculate/', RecalculateRiskView.as_view(), name='case_recalculate'),
]
