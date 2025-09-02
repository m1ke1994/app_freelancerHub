from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .views import ProposalViewSet, AssignmentViewSet, StatsView

@api_view(["GET"])
def ping(request):
    return Response({"ok": True, "app": "offer"})

router = DefaultRouter()
router.register(r"proposals", ProposalViewSet, basename="proposal")
router.register(r"assignments", AssignmentViewSet, basename="assignment")

urlpatterns = [
    path("", include(router.urls)),
    path("proposals/stats", StatsView.as_view(), name="proposals-stats"),
    path("offer/ping/", ping, name="offer-ping"),
]
