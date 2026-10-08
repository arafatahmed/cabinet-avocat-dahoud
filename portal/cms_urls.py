from django.urls import path

from . import views


app_name = "cms"

urlpatterns = [
    path("connexion/", views.StaffLoginView.as_view(), name="login"),
    path("deconnexion/", views.staff_logout, name="logout"),
    path("", views.cms_dashboard, name="dashboard"),
    path("site/", views.cms_site_settings, name="site_settings"),
    path("rendez-vous/", views.cms_appointments, name="appointments"),
    path(
        "rendez-vous/<int:pk>/",
        views.cms_appointments,
        name="appointment_update",
    ),
    path("<slug:section>/", views.cms_manage_content, name="content"),
    path(
        "<slug:section>/<int:pk>/",
        views.cms_manage_content,
        name="content_edit",
    ),
]
