from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from django.db.models import Q
from .models import LandAcquisitionCase, SECTORS, STAGES, RISK_LEVELS
from .forms import LandAcquisitionCaseForm

class CaseListView(ListView):
    model = LandAcquisitionCase
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        risk_level = self.request.GET.get('risk_level', '').strip()
        sector = self.request.GET.get('sector', '').strip()
        stage = self.request.GET.get('stage', '').strip()
        is_delayed = self.request.GET.get('is_delayed', '').strip()

        if query:
            qs = qs.filter(
                Q(project_name__icontains=query) |
                Q(case_number__icontains=query) |
                Q(district__icontains=query) |
                Q(taluk_village__icontains=query)
            )
        if risk_level:
            qs = qs.filter(risk_level=risk_level)
        if sector:
            qs = qs.filter(sector=sector)
        if stage:
            qs = qs.filter(current_stage=stage)
        if is_delayed in ['1', 'true', 'True']:
            qs = qs.filter(is_delayed=True)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sectors'] = SECTORS
        context['stages'] = STAGES
        context['risk_levels'] = RISK_LEVELS
        context['total_count'] = LandAcquisitionCase.objects.count()
        context['filtered_count'] = self.get_queryset().count()
        return context

class CaseDetailView(DetailView):
    model = LandAcquisitionCase
    template_name = 'cases/case_detail.html'
    context_object_name = 'case'

class CaseCreateView(CreateView):
    model = LandAcquisitionCase
    form_class = LandAcquisitionCaseForm
    template_name = 'cases/case_form.html'

    def form_valid(self, form):
        self.object = form.save()
        # Automatically run AI risk assessment on new case
        try:
            self.object.run_risk_assessment()
            messages.success(
                self.request,
                f"Case '{self.object.project_name}' created successfully with {self.object.risk_level} Risk score ({self.object.risk_score}/100)."
            )
        except Exception as e:
            messages.warning(self.request, f"Case saved, but ML assessment encountered an error: {e}")
        return redirect(self.object.get_absolute_url())

class CaseUpdateView(UpdateView):
    model = LandAcquisitionCase
    form_class = LandAcquisitionCaseForm
    template_name = 'cases/case_form.html'

    def form_valid(self, form):
        self.object = form.save()
        # Automatically recalculate AI risk assessment on update
        try:
            self.object.run_risk_assessment()
            messages.success(
                self.request,
                f"Case '{self.object.project_name}' updated. AI re-assessed risk: {self.object.risk_level} ({self.object.risk_score}/100)."
            )
        except Exception as e:
            messages.warning(self.request, f"Case updated, but ML assessment encountered an error: {e}")
        return redirect(self.object.get_absolute_url())

class CaseDeleteView(DeleteView):
    model = LandAcquisitionCase
    template_name = 'cases/case_confirm_delete.html'
    success_url = reverse_lazy('case_list')

    def delete(self, request, *args, **kwargs):
        messages.info(request, "Land acquisition case deleted successfully.")
        return super().delete(request, *args, **kwargs)

class RecalculateRiskView(View):
    def post(self, request, pk):
        case = get_object_or_404(LandAcquisitionCase, pk=pk)
        try:
            case.run_risk_assessment()
            messages.success(
                request,
                f"AI Risk Assessment updated for {case.project_name}. New Score: {case.risk_score}/100 ({case.risk_level} Risk)."
            )
        except Exception as e:
            messages.error(request, f"Failed to recalculate risk: {e}")
        return redirect('case_detail', pk=pk)
