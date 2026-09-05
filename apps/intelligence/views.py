import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from apps.cases.models import LandAcquisitionCase
from .services import simulate_what_if

@require_POST
def api_simulate_case(request, pk):
    """
    JSON API endpoint to evaluate scenario simulations on the fly.
    """
    try:
        case = LandAcquisitionCase.objects.get(pk=pk)
    except LandAcquisitionCase.DoesNotExist:
        return JsonResponse({'error': 'Case not found'}, status=404)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        payload = request.POST.dict()

    result = simulate_what_if(case, payload)
    return JsonResponse(result)
