import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from base.services.generate_with_ai import GenerateIA



@csrf_exempt
def generate_swot_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")
    try:
        _generator = GenerateIA()
        body = json.loads(request.body.decode("utf-8") or "{}")
        context = body.get("context", "Banque & Finance")
        swot = _generator.generate_swot(context)
        return JsonResponse(swot)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def generate_scenarios_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")
    try:
        _generator = GenerateIA()
        body = json.loads(request.body.decode("utf-8") or "{}")
        business_values = body.get("business_values", [])
        risk_sources = body.get("risk_sources", [])
        scenarios = _generator.generate_strategic_scenarios(business_values, risk_sources)
        return JsonResponse(scenarios, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def suggest_assets_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")
    try:
        _generator = GenerateIA()
        body = json.loads(request.body.decode("utf-8") or "{}")
        context = body.get("context", "Banque & Finance")
        assets = _generator.suggest_assets(context)
        return JsonResponse(assets, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def generate_measures_view(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")
    try:
        _generator = GenerateIA()
        body = json.loads(request.body.decode("utf-8") or "{}")
        risks = body.get("risks", [])
        measures = _generator.generate_measures(risks)
        return JsonResponse(measures, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
