from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.db.models import Count, Avg, Q
from apps.cases.models import LandAcquisitionCase

class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cases = LandAcquisitionCase.objects.all()

        total = cases.count()
        ongoing = cases.exclude(current_stage='Physical Possession').count()
        delayed = cases.filter(is_delayed=True).count()

        high_risk = cases.filter(risk_level='High').count()
        medium_risk = cases.filter(risk_level='Medium').count()
        low_risk = cases.filter(risk_level='Low').count()

        avg_risk_score = round(cases.aggregate(avg=Avg('risk_score'))['avg'] or 0, 1)

        # Stage bottleneck breakdown
        stage_breakdown = cases.exclude(predicted_delay_stage='None').values('predicted_delay_stage').annotate(
            count=Count('id')
        ).order_by('-count')

        # Sector distribution with high risk count
        sector_breakdown = cases.values('sector').annotate(
            total=Count('id'),
            high_risk_count=Count('id', filter=Q(risk_level='High'))
        ).order_by('-total')

        # Cases requiring immediate administrative intervention (High risk or Critical warnings)
        intervention_watchlist = cases.filter(
            Q(risk_level='High') | Q(warning_severity__in=['CRITICAL', 'HIGH'])
        ).order_by('-risk_score')[:8]

        context.update({
            'total_cases': total,
            'ongoing_cases': ongoing,
            'delayed_cases': delayed,
            'high_risk_cases': high_risk,
            'medium_risk_cases': medium_risk,
            'low_risk_cases': low_risk,
            'avg_risk_score': avg_risk_score,
            'stage_breakdown': stage_breakdown,
            'sector_breakdown': sector_breakdown,
            'intervention_watchlist': intervention_watchlist,
        })
        return context

class DashboardChartsApiView(View):
    def get(self, request):
        cases = LandAcquisitionCase.objects.all()

        # 1. Risk Distribution Data
        risk_counts = {
            'Low': cases.filter(risk_level='Low').count(),
            'Medium': cases.filter(risk_level='Medium').count(),
            'High': cases.filter(risk_level='High').count(),
        }

        # 2. Predicted Bottleneck Stages Data
        stage_counts = {}
        for item in cases.values('predicted_delay_stage').annotate(c=Count('id')):
            stg = item['predicted_delay_stage']
            if stg and stg != 'None':
                stage_counts[stg] = item['c']

        # 3. Sector Delay & Risk Comparison
        sectors = []
        sector_avg_risk = []
        sector_delayed_rates = []
        for s in cases.values('sector').annotate(avg_r=Avg('risk_score'), total=Count('id'), delayed_cnt=Count('id', filter=Q(is_delayed=True))):
            sectors.append(s['sector'])
            sector_avg_risk.append(round(s['avg_r'] or 0, 1))
            delayed_rate = round((s['delayed_cnt'] / s['total'] * 100) if s['total'] else 0, 1)
            sector_delayed_rates.append(delayed_rate)

        return JsonResponse({
            'risk_distribution': {
                'labels': list(risk_counts.keys()),
                'data': list(risk_counts.values())
            },
            'stage_breakdown': {
                'labels': list(stage_counts.keys()),
                'data': list(stage_counts.values())
            },
            'sector_analytics': {
                'labels': sectors,
                'avg_risk': sector_avg_risk,
                'delayed_rates': sector_delayed_rates
            }
        })
