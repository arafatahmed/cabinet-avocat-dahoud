from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView


urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("admin/", admin.site.urls),
    path(
        "connexion/",
        auth_views.LoginView.as_view(template_name="portal/login.html"),
        name="login",
    ),
    path(
        "deconnexion/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "mot-de-passe-oublie/",
        auth_views.PasswordResetView.as_view(
            template_name="portal/password_reset.html",
            email_template_name="portal/password_reset_email.txt",
        ),
        name="password_reset",
    ),
    path(
        "mot-de-passe-envoye/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="portal/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reinitialisation/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="portal/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "mot-de-passe-modifie/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="portal/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("gestion/", include("portal.cms_urls")),
    path("espace-client/", include("portal.urls")),
]
