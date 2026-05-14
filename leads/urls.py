from django.urls import path, include
from rest_framework.routers import DefaultRouter
from leads.views import LeadViewSet, BotRateProxyView

router = DefaultRouter()
router.register(r"", LeadViewSet, basename="lead")

urlpatterns = [
    path("rate/", BotRateProxyView.as_view(), name="bot-rate-proxy"),
    path("", include(router.urls)),
]
