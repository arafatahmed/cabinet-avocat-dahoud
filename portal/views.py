from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import SuspiciousFileOperation
from django.http import JsonResponse
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test

from .cms import LANGUAGES, TEXT_FIELDS
from .cms_forms import (
    GalleryPhotoForm,
    PracticeAreaForm,
    PublicationForm,
    SiteSettingsForm,
    StaffAuthenticationForm,
    TeamMemberForm,
)
from .forms import (
    AppointmentRequestForm,
    ClientMessageForm,
    DocumentUploadForm,
)
from .models import (
    AppointmentRequest,
    ClientMessage,
    ClientProfile,
    GalleryPhoto,
    Matter,
    PracticeArea,
    PrivateDocument,
    Publication,
    SiteSettings,
    TeamMember,
)

staff_required = user_passes_test(
    lambda user: user.is_authenticated and user.is_active and user.is_staff,
    login_url="cms:login",
)

CMS_SECTIONS = {
    "expertises": {
        "title": "Domaines d’expertise",
        "description": "Présentez les domaines d’intervention du cabinet en français, en arabe et en anglais.",
        "model": PracticeArea,
        "form": PracticeAreaForm,
        "label": "domaine",
    },
    "galerie": {
        "title": "Photographies",
        "description": "Gérez les photos d’architecture, des locaux et des références juridiques du site.",
        "model": GalleryPhoto,
        "form": GalleryPhotoForm,
        "label": "photo",
    },
    "equipe": {
        "title": "Équipe",
        "description": "Présentez les avocats et leurs parcours dans les trois langues du site.",
        "model": TeamMember,
        "form": TeamMemberForm,
        "label": "membre",
    },
    "publications": {
        "title": "Publications",
        "description": "Publiez les actualités et informations juridiques du cabinet.",
        "model": Publication,
        "form": PublicationForm,
        "label": "publication",
    },
}


@login_required
def dashboard(request):
    profile = get_object_or_404(ClientProfile, user=request.user)
    matters = profile.matters.prefetch_related("updates").all()
    context = {
        "profile": profile,
        "matters": matters,
        "active_count": matters.exclude(status=Matter.Status.CLOSED).count(),
        "upcoming_hearings": matters.filter(
            next_hearing__gte=timezone.now()
        ).order_by("next_hearing")[:3],
        "appointments": profile.appointment_requests.all()[:4],
        "appointment_form": AppointmentRequestForm(),
    }
    return render(request, "portal/dashboard.html", context)


@login_required
def matter_detail(request, pk):
    profile = get_object_or_404(ClientProfile, user=request.user)
    matter = get_object_or_404(
        Matter.objects.select_related("client", "client__user"),
        pk=pk,
        client=profile,
    )
    context = {
        "profile": profile,
        "matter": matter,
        "updates": matter.updates.filter(visible_to_client=True),
        "documents": matter.documents.filter(visible_to_client=True),
        "messages_list": matter.messages.select_related("author"),
        "message_form": ClientMessageForm(),
        "document_form": DocumentUploadForm(),
    }
    return render(request, "portal/matter_detail.html", context)


@login_required
def send_message(request, pk):
    if request.method != "POST":
        raise Http404
    profile = get_object_or_404(ClientProfile, user=request.user)
    matter = get_object_or_404(Matter, pk=pk, client=profile)
    form = ClientMessageForm(request.POST)
    if form.is_valid():
        ClientMessage.objects.create(
            matter=matter,
            author=request.user,
            is_from_client=True,
            content=form.cleaned_data["content"],
        )
        messages.success(request, "Votre message a été envoyé au cabinet.")
    else:
        messages.error(request, "Votre message n'a pas pu être envoyé.")
    return redirect("portal:matter_detail", pk=matter.pk)


@login_required
def upload_document(request, pk):
    if request.method != "POST":
        raise Http404
    profile = get_object_or_404(ClientProfile, user=request.user)
    matter = get_object_or_404(Matter, pk=pk, client=profile)
    form = DocumentUploadForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.matter = matter
        document.uploaded_by = request.user
        document.save()
        messages.success(request, "Votre document a été déposé en toute sécurité.")
    else:
        messages.error(request, "Le document n'a pas pu être déposé. Vérifiez son format et sa taille (10 Mo maximum).")
    return redirect("portal:matter_detail", pk=matter.pk)


@login_required
def download_document(request, pk):
    profile = get_object_or_404(ClientProfile, user=request.user)
    document = get_object_or_404(
        PrivateDocument.objects.select_related("matter"),
        pk=pk,
        matter__client=profile,
        visible_to_client=True,
    )
    try:
        file_handle = document.file.open("rb")
    except (FileNotFoundError, SuspiciousFileOperation) as exc:
        raise Http404("Ce document n'est pas disponible.") from exc
    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=Path(document.file.name).name,
        content_type="application/octet-stream",
    )


@login_required
def request_appointment(request):
    if request.method != "POST":
        raise Http404
    profile = get_object_or_404(ClientProfile, user=request.user)
    form = AppointmentRequestForm(request.POST)
    if form.is_valid():
        appointment = form.save(commit=False)
        appointment.client = profile
        appointment.save()
        messages.success(
            request, "Votre demande de rendez-vous a été transmise au cabinet."
        )
    else:
        messages.error(
            request, "La demande n'a pas été enregistrée. Vérifiez la date et les champs."
        )
    return redirect("portal:dashboard")


class StaffLoginView(LoginView):
    template_name = "portal/cms_login.html"
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse("cms:dashboard")


@never_cache
def staff_logout(request):
    if request.method != "POST":
        raise Http404
    logout(request)
    return redirect("cms:login")


@staff_required
def cms_dashboard(request):
    context = {
        "client_count": ClientProfile.objects.count(),
        "matter_count": Matter.objects.count(),
        "open_matter_count": Matter.objects.exclude(
            status=Matter.Status.CLOSED
        ).count(),
        "pending_appointments": AppointmentRequest.objects.filter(
            status=AppointmentRequest.Status.PENDING
        ).select_related("client").order_by("-created_at")[:6],
        "sections": CMS_SECTIONS,
    }
    return render(request, "portal/cms_dashboard.html", context)


@staff_required
def cms_site_settings(request):
    instance, _created = SiteSettings.objects.get_or_create(pk=1)
    form = SiteSettingsForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Les coordonnées et contenus du site ont été enregistrés.")
        return redirect("cms:site_settings")
    return render(
        request,
        "portal/cms_site_settings.html",
        {"form": form, "languages": LANGUAGES, "text_fields": TEXT_FIELDS},
    )


@staff_required
def cms_manage_content(request, section, pk=None):
    config = CMS_SECTIONS.get(section)
    if config is None:
        raise Http404
    model = config["model"]
    obj = get_object_or_404(model, pk=pk) if pk is not None else None
    if request.method == "POST" and request.POST.get("action") == "delete":
        if obj is None:
            raise Http404
        obj.delete()
        messages.success(request, f"Le contenu « {config['label']} » a été supprimé.")
        return redirect("cms:content", section=section)

    form = config["form"](
        request.POST or None,
        instance=obj,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Les modifications ont été enregistrées.")
        return redirect("cms:content", section=section)

    items = model.objects.all()
    return render(
        request,
        "portal/cms_content.html",
        {
            "section": section,
            "config": config,
            "form": form,
            "item": obj,
            "items": items,
            "is_editing": obj is not None,
        },
    )


@staff_required
def cms_appointments(request, pk=None):
    if request.method == "POST" and pk is not None:
        appointment = get_object_or_404(AppointmentRequest, pk=pk)
        new_status = request.POST.get("status")
        if new_status in AppointmentRequest.Status.values:
            appointment.status = new_status
            appointment.save(update_fields=["status"])
            messages.success(request, "Le statut du rendez-vous a été modifié.")
        else:
            messages.error(request, "Le statut choisi n'est pas valide.")
        return redirect("cms:appointments")
    return render(
        request,
        "portal/cms_appointments.html",
        {
            "appointments": AppointmentRequest.objects.select_related(
                "client", "client__user"
            ).all(),
            "statuses": AppointmentRequest.Status.choices,
        },
    )


def public_site_api(request):
    site_settings = SiteSettings.objects.filter(pk=1).first()
    areas = [
        {
            "title": [area.title_fr, area.title_ar or area.title_fr, area.title_en or area.title_fr],
            "description": [
                area.description_fr,
                area.description_ar or area.description_fr,
                area.description_en or area.description_fr,
            ],
            "icon": area.icon,
        }
        for area in PracticeArea.objects.filter(is_active=True)
    ]
    photos = [
        {
            "src": photo.image_url,
            "fr": photo.caption_fr,
            "ar": photo.caption_ar or photo.caption_fr,
            "en": photo.caption_en or photo.caption_fr,
            "slide": photo.is_slide,
        }
        for photo in GalleryPhoto.objects.filter(is_active=True)
    ]
    team = [
        {
            "name": [member.name_fr, member.name_ar or member.name_fr, member.name_en or member.name_fr],
            "title": [member.title_fr, member.title_ar or member.title_fr, member.title_en or member.title_fr],
            "bio": [member.bio_fr, member.bio_ar or member.bio_fr, member.bio_en or member.bio_fr],
            "credentials": [
                member.credentials_fr,
                member.credentials_ar or member.credentials_fr,
                member.credentials_en or member.credentials_fr,
            ],
            "portrait": member.portrait_url,
        }
        for member in TeamMember.objects.filter(is_active=True)
    ]
    publications = [
        {
            "category": [
                publication.category_fr,
                publication.category_ar or publication.category_fr,
                publication.category_en or publication.category_fr,
            ],
            "title": [
                publication.title_fr,
                publication.title_ar or publication.title_fr,
                publication.title_en or publication.title_fr,
            ],
            "excerpt": [
                publication.excerpt_fr,
                publication.excerpt_ar or publication.excerpt_fr,
                publication.excerpt_en or publication.excerpt_fr,
            ],
        }
        for publication in Publication.objects.filter(is_active=True)
    ]
    contact = {}
    translations = {}
    if site_settings:
        translations = {
            key: [
                values.get(language, "")
                for language in ("fr", "ar", "en")
            ]
            for key, values in site_settings.translations.items()
            if isinstance(values, dict)
        }
        contact = {
            "tel": site_settings.telephone,
            "whatsapp": site_settings.whatsapp,
            "fixe": site_settings.telephone_fixe,
            "email": site_settings.email,
            "web": site_settings.site_web,
            "address": site_settings.adresse,
            "hours": site_settings.heures,
            "mapsQuery": site_settings.adresse_carte,
        }
    return JsonResponse(
        {
            "translations": translations,
            "contact": contact,
            "practiceAreas": areas,
            "photos": photos,
            "team": team,
            "publications": publications,
        }
    )
