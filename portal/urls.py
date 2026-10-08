from django.urls import path

from . import views


app_name = "portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dossiers/<int:pk>/", views.matter_detail, name="matter_detail"),
    path(
        "dossiers/<int:pk>/message/",
        views.send_message,
        name="send_message",
    ),
    path(
        "dossiers/<int:pk>/documents/",
        views.upload_document,
        name="upload_document",
    ),
    path(
        "documents/<int:pk>/telecharger/",
        views.download_document,
        name="download_document",
    ),
    path("rendez-vous/", views.request_appointment, name="request_appointment"),
    path("api/public-site/", views.public_site_api, name="public_site_api"),
]
