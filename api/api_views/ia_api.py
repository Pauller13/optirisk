from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from base.services.generate_with_ai import GenerateIA


# =========================
# SWAGGER SCHEMAS
# =========================

swot_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "context": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Business context",
            example="Banque & Finance"
        ),
    },
)

scenario_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "business_values": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_STRING),
            example=["Disponibilité", "Confidentialité"],
        ),
        "risk_sources": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_STRING),
            example=["Cyberattaque", "Erreur humaine"],
        ),
    },
)

assets_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "context": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="Banque & Finance"
        ),
    },
)

measures_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "risks": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_STRING),
            example=["Ransomware", "Fuite de données"],
        ),
    },
)


# =========================
# VIEWS
# =========================

@swagger_auto_schema(
    method="post",
    request_body=swot_request_schema,
    responses={200: openapi.Response("SWOT generated")},
)
@api_view(["POST"])
def generate_swot_view(request):
    try:
        generator = GenerateIA()
        context = request.data.get("context", "Banque & Finance")
        swot = generator.generate_swot(context)
        return Response(swot)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    request_body=scenario_request_schema,
    responses={200: openapi.Response("Strategic scenarios generated")},
)
@api_view(["POST"])
def generate_scenarios_view(request):
    try:
        generator = GenerateIA()
        business_values = request.data.get("business_values", [])
        risk_sources = request.data.get("risk_sources", [])
        scenarios = generator.generate_strategic_scenarios(business_values, risk_sources)
        return Response(scenarios)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    request_body=assets_request_schema,
    responses={200: openapi.Response("Assets suggested")},
)
@api_view(["POST"])
def suggest_assets_view(request):
    try:
        generator = GenerateIA()
        context = request.data.get("context", "Banque & Finance")
        assets = generator.suggest_assets(context)
        return Response(assets)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="post",
    request_body=measures_request_schema,
    responses={200: openapi.Response("Measures generated")},
)
@api_view(["POST"])
def generate_measures_view(request):
    try:
        generator = GenerateIA()
        risks = request.data.get("risks", [])
        measures = generator.generate_measures(risks)
        return Response(measures)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)