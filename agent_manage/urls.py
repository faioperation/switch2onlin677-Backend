from django.urls import path
from .views import AgentBehaviorConfigView

urlpatterns = [
    path("agent-behavior/", AgentBehaviorConfigView.as_view(), name="agent-behavior"),
]
