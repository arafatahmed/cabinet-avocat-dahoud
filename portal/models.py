from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
ALLOWED_DOCUMENT_EXTENSIONS = ["pdf", "doc", "docx", "jpg", "jpeg", "png"]


def validate_document_size(uploaded_file):
    if uploaded_file.size > MAX_DOCUMENT_SIZE:
        raise ValidationError("Le fichier ne doit pas dépasser 10 Mo.")


def document_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"clients/{instance.matter.client_id}/dossiers/{instance.matter_id}/{uuid4().hex}{extension}"


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    full_name = models.CharField("nom complet", max_length=160)
    phone = models.CharField("téléphone", max_length=32, blank=True)
    created_at = models.DateTimeField("créé le", auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "client"
        verbose_name_plural = "clients"

    def __str__(self):
        return self.full_name


class Matter(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "En cours"
        WAITING = "waiting", "En attente"
        CLOSED = "closed", "Clôturé"

    class Category(models.TextChoices):
        BUSINESS = "business", "Droit des affaires"
        EMPLOYMENT = "employment", "Droit du travail"
        CRIMINAL = "criminal", "Droit pénal"
        FAMILY = "family", "Famille et personnes"
        PROPERTY = "property", "Foncier et immobilier"
        ADMINISTRATIVE = "administrative", "Droit administratif"
        OTHER = "other", "Autre"

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.PROTECT,
        related_name="matters",
        verbose_name="client",
    )
    reference = models.CharField("référence", max_length=40, unique=True)
    title = models.CharField("intitulé du dossier", max_length=180)
    category = models.CharField(
        "domaine", max_length=24, choices=Category.choices, default=Category.OTHER
    )
    status = models.CharField(
        "statut", max_length=12, choices=Status.choices, default=Status.OPEN
    )
    court = models.CharField("juridiction", max_length=160, blank=True)
    responsible_lawyer = models.CharField("avocat responsable", max_length=160, blank=True)
    opened_at = models.DateField("ouvert le", auto_now_add=True)
    next_hearing = models.DateTimeField("prochaine audience", null=True, blank=True)
    summary = models.TextField("résumé", blank=True)
    updated_at = models.DateTimeField("mis à jour le", auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "dossier"
        verbose_name_plural = "dossiers"

    def __str__(self):
        return f"{self.reference} — {self.title}"


class CaseUpdate(models.Model):
    matter = models.ForeignKey(
        Matter,
        on_delete=models.CASCADE,
        related_name="updates",
        verbose_name="dossier",
    )
    title = models.CharField("titre", max_length=180)
    body = models.TextField("détail")
    visible_to_client = models.BooleanField("visible par le client", default=True)
    created_at = models.DateTimeField("date", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "événement du dossier"
        verbose_name_plural = "événements du dossier"

    def __str__(self):
        return f"{self.matter.reference} — {self.title}"


class PrivateDocument(models.Model):
    matter = models.ForeignKey(
        Matter,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="dossier",
    )
    title = models.CharField("nom du document", max_length=180)
    file = models.FileField(
        "fichier privé",
        upload_to=document_upload_path,
        validators=[
            FileExtensionValidator(ALLOWED_DOCUMENT_EXTENSIONS),
            validate_document_size,
        ],
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_documents",
    )
    visible_to_client = models.BooleanField("visible par le client", default=True)
    uploaded_at = models.DateTimeField("déposé le", auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "document privé"
        verbose_name_plural = "documents privés"

    def __str__(self):
        return f"{self.matter.reference} — {self.title}"


class ClientMessage(models.Model):
    matter = models.ForeignKey(
        Matter,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="dossier",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="matter_messages",
    )
    is_from_client = models.BooleanField("envoyé par le client", default=False)
    content = models.TextField("message", max_length=5000)
    created_at = models.DateTimeField("envoyé le", auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "message de dossier"
        verbose_name_plural = "messages de dossier"

    def __str__(self):
        return f"Message — {self.matter.reference}"


class AppointmentRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "À confirmer"
        CONFIRMED = "confirmed", "Confirmé"
        DECLINED = "declined", "Non retenu"

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="appointment_requests",
        verbose_name="client",
    )
    subject = models.CharField("motif", max_length=160)
    preferred_at = models.DateTimeField("date souhaitée")
    details = models.TextField("précisions", blank=True, max_length=2000)
    status = models.CharField(
        "statut", max_length=12, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField("demandé le", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "demande de rendez-vous"
        verbose_name_plural = "demandes de rendez-vous"

    def __str__(self):
        return f"{self.client} — {self.subject}"


class SiteSettings(models.Model):
    translations = models.JSONField(
        "textes du site par langue",
        default=dict,
        blank=True,
        help_text="Contenus éditoriaux du site public, en français, arabe et anglais.",
    )
    telephone = models.CharField("téléphone", max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=40, blank=True)
    telephone_fixe = models.CharField("téléphone fixe", max_length=80, blank=True)
    email = models.EmailField("e-mail", blank=True)
    site_web = models.CharField("site internet", max_length=160, blank=True)
    adresse = models.CharField("adresse", max_length=240, blank=True)
    heures = models.CharField("horaires", max_length=180, blank=True)
    adresse_carte = models.CharField(
        "adresse de recherche sur la carte", max_length=240, blank=True
    )
    updated_at = models.DateTimeField("mis à jour le", auto_now=True)

    class Meta:
        verbose_name = "réglages du site"
        verbose_name_plural = "réglages du site"

    def __str__(self):
        return "Contenu et coordonnées publiques"


class PracticeArea(models.Model):
    title_fr = models.CharField("titre (français)", max_length=120)
    title_ar = models.CharField("titre (arabe)", max_length=120, blank=True)
    title_en = models.CharField("titre (anglais)", max_length=120, blank=True)
    description_fr = models.TextField("description (français)")
    description_ar = models.TextField("description (arabe)", blank=True)
    description_en = models.TextField("description (anglais)", blank=True)
    icon = models.PositiveSmallIntegerField(
        "icône", choices=[(i, f"Symbole {i}") for i in range(1, 7)], default=1
    )
    position = models.PositiveSmallIntegerField("ordre", default=0)
    is_active = models.BooleanField("publiée", default=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "expertise"
        verbose_name_plural = "expertises"

    def __str__(self):
        return self.title_fr


class GalleryPhoto(models.Model):
    image_url = models.CharField(
        "URL HTTPS de l'image",
        max_length=500,
        help_text="Utilisez une URL HTTPS ou un chemin /static/images/... du site.",
    )
    caption_fr = models.CharField("légende (français)", max_length=160)
    caption_ar = models.CharField("légende (arabe)", max_length=160, blank=True)
    caption_en = models.CharField("légende (anglais)", max_length=160, blank=True)
    position = models.PositiveSmallIntegerField("ordre", default=0)
    is_slide = models.BooleanField("utiliser dans le diaporama", default=False)
    is_active = models.BooleanField("publiée", default=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "photo de la galerie"
        verbose_name_plural = "photos de la galerie"

    def __str__(self):
        return self.caption_fr


class TeamMember(models.Model):
    name_fr = models.CharField("nom (français)", max_length=160)
    name_ar = models.CharField("nom (arabe)", max_length=160, blank=True)
    name_en = models.CharField("nom (anglais)", max_length=160, blank=True)
    title_fr = models.CharField("titre (français)", max_length=180, blank=True)
    title_ar = models.CharField("titre (arabe)", max_length=180, blank=True)
    title_en = models.CharField("titre (anglais)", max_length=180, blank=True)
    bio_fr = models.TextField("présentation (français)", blank=True)
    bio_ar = models.TextField("présentation (arabe)", blank=True)
    bio_en = models.TextField("présentation (anglais)", blank=True)
    credentials_fr = models.JSONField(
        "distinctions (français, liste)", default=list, blank=True
    )
    credentials_ar = models.JSONField(
        "distinctions (arabe, liste)", default=list, blank=True
    )
    credentials_en = models.JSONField(
        "distinctions (anglais, liste)", default=list, blank=True
    )
    portrait_url = models.URLField(
        "URL HTTPS du portrait",
        max_length=500,
        blank=True,
        help_text="Facultatif. Laissez vide pour afficher l'identité graphique du cabinet.",
    )
    position = models.PositiveSmallIntegerField("ordre", default=0)
    is_active = models.BooleanField("publié", default=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "membre de l'équipe"
        verbose_name_plural = "équipe"

    def __str__(self):
        return self.name_fr


class Publication(models.Model):
    category_fr = models.CharField("rubrique (français)", max_length=100)
    category_ar = models.CharField("rubrique (arabe)", max_length=100, blank=True)
    category_en = models.CharField("rubrique (anglais)", max_length=100, blank=True)
    title_fr = models.CharField("titre (français)", max_length=200)
    title_ar = models.CharField("titre (arabe)", max_length=200, blank=True)
    title_en = models.CharField("titre (anglais)", max_length=200, blank=True)
    excerpt_fr = models.TextField("résumé (français)")
    excerpt_ar = models.TextField("résumé (arabe)", blank=True)
    excerpt_en = models.TextField("résumé (anglais)", blank=True)
    published_at = models.DateField("date de publication", null=True, blank=True)
    position = models.PositiveSmallIntegerField("ordre", default=0)
    is_active = models.BooleanField("publiée", default=True)

    class Meta:
        ordering = ["position", "-published_at", "id"]
        verbose_name = "publication"
        verbose_name_plural = "publications"

    def __str__(self):
        return self.title_fr
