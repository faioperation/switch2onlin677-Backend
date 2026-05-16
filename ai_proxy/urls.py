from django.urls import path
from ai_proxy.views import (
    RateProxyView,
    PromptProxyView,
    KnowledgeProxyView,
    KnowledgeUploadProxyView,
    KnowledgeDetailProxyView,
    ProductTemplateProxyView,
    ProductUploadProxyView,
)

urlpatterns = [
    path("rate/", RateProxyView.as_view(), name="ai-rate-proxy"),
    path("prompt/", PromptProxyView.as_view(), name="ai-prompt-proxy"),
    path("knowledge/", KnowledgeProxyView.as_view(), name="ai-knowledge-proxy"),
    path("knowledge/upload/", KnowledgeUploadProxyView.as_view(), name="ai-knowledge-upload-proxy"),
    path("knowledge/<str:knowledge_id>/", KnowledgeDetailProxyView.as_view(), name="ai-knowledge-detail-proxy"),
    path("products/upload-template/", ProductTemplateProxyView.as_view(), name="ai-product-template-proxy"),
    path("products/upload/", ProductUploadProxyView.as_view(), name="ai-product-upload-proxy"),
]
