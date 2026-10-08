from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    ClientProfile,
    GalleryPhoto,
    Matter,
    PracticeArea,
    PrivateDocument,
    SiteSettings,
)


@override_settings(
    SECURE_SSL_REDIRECT=False,
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class ClientPortalAccessTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.client_user = user_model.objects.create_user(
            username="client-a", password="Strong-test-password-42"
        )
        self.client_profile = ClientProfile.objects.create(
            user=self.client_user, full_name="Client A"
        )
        self.other_user = user_model.objects.create_user(
            username="client-b", password="Strong-test-password-42"
        )
        self.other_profile = ClientProfile.objects.create(
            user=self.other_user, full_name="Client B"
        )
        self.staff_user = user_model.objects.create_user(
            username="cabinet-admin",
            password="Secure-cabinet-password-47",
            is_staff=True,
        )
        self.matter = Matter.objects.create(
            client=self.client_profile,
            reference="CD-2026-001",
            title="Dossier confidentiel",
        )

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("portal:dashboard"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('portal:dashboard')}"
        )

    def test_existing_site_is_served_from_the_django_root(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Espace client")

    def test_public_api_exposes_editor_managed_website_content(self):
        SiteSettings.objects.update_or_create(
            pk=1,
            defaults={"translations": {"s1t": {"fr": "Le site dynamique"}}},
        )
        PracticeArea.objects.create(
            title_fr="Droit public",
            title_ar="القانون العام",
            title_en="Public law",
            description_fr="Conseil et représentation.",
            description_ar="استشارات وتمثيل.",
            description_en="Advice and representation.",
            icon=1,
        )
        GalleryPhoto.objects.create(
            image_url="/static/images/mosque-aerial.jpg",
            caption_fr="Architecture",
            caption_ar="عمارة",
            caption_en="Architecture",
            is_slide=True,
        )
        response = self.client.get(reverse("portal:public_site_api"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["translations"]["s1t"], ["Le site dynamique", "", ""])
        self.assertEqual(data["practiceAreas"][0]["title"][1], "القانون العام")
        self.assertEqual(data["photos"][0]["src"], "/static/images/mosque-aerial.jpg")

    def test_custom_management_area_requires_staff_access(self):
        response = self.client.get(reverse("cms:dashboard"))
        self.assertRedirects(
            response, f"{reverse('cms:login')}?next={reverse('cms:dashboard')}"
        )

    def test_client_account_cannot_sign_in_to_custom_management_area(self):
        response = self.client.post(
            reverse("cms:login"),
            {"username": "client-a", "password": "Strong-test-password-42"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn("Cet espace est réservé", str(response.context["form"].errors))

    def test_staff_can_open_custom_management_dashboard(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("cms:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestion du site")

    def test_staff_can_update_homepage_content(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse("cms:site_settings"),
            {
                "telephone": "+222 47 03 03 04",
                "whatsapp": "+222 31 03 03 06",
                "telephone_fixe": "",
                "email": "dahoudavocat@gmail.com",
                "site_web": "www.avocat-dahoud.com",
                "adresse": "Nouakchott",
                "heures": "Sur rendez-vous",
                "adresse_carte": "Nouakchott",
                "text_s1t_fr": "Une équipe engagée",
                "text_s1t_ar": "فريق ملتزم",
                "text_s1t_en": "A dedicated legal team",
            },
        )
        self.assertRedirects(response, reverse("cms:site_settings"))
        self.assertEqual(
            SiteSettings.objects.get(pk=1).translations["s1t"]["fr"],
            "Une équipe engagée",
        )

    def test_client_can_only_view_owned_matters(self):
        self.client.force_login(self.client_user)
        own_response = self.client.get(
            reverse("portal:matter_detail", args=[self.matter.pk])
        )
        other_matter = Matter.objects.create(
            client=self.other_profile,
            reference="CD-2026-002",
            title="Autre dossier",
        )
        foreign_response = self.client.get(
            reverse("portal:matter_detail", args=[other_matter.pk])
        )
        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(foreign_response.status_code, 404)

    def test_dashboard_shows_only_the_signed_in_clients_matters(self):
        Matter.objects.create(
            client=self.other_profile,
            reference="CD-2026-002",
            title="Dossier confidentiel B",
        )
        self.client.force_login(self.client_user)
        response = self.client.get(reverse("portal:dashboard"))
        self.assertContains(response, "CD-2026-001")
        self.assertNotContains(response, "CD-2026-002")

    def test_client_can_send_a_message_on_owned_matter(self):
        self.client.force_login(self.client_user)
        response = self.client.post(
            reverse("portal:send_message", args=[self.matter.pk]),
            {"content": "Je vous transmets les pièces demandées."},
        )
        self.assertRedirects(
            response, reverse("portal:matter_detail", args=[self.matter.pk])
        )
        self.assertEqual(self.matter.messages.count(), 1)
        self.assertTrue(self.matter.messages.get().is_from_client)

    def test_client_cannot_download_another_clients_document(self):
        other_matter = Matter.objects.create(
            client=self.other_profile,
            reference="CD-2026-002",
            title="Autre dossier",
        )
        document = PrivateDocument.objects.create(
            matter=other_matter,
            title="Document confidentiel",
            file="private/secret.pdf",
        )
        self.client.force_login(self.client_user)
        response = self.client.get(
            reverse("portal:download_document", args=[document.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_client_cannot_upload_to_another_clients_matter(self):
        other_matter = Matter.objects.create(
            client=self.other_profile,
            reference="CD-2026-002",
            title="Autre dossier",
        )
        self.client.force_login(self.client_user)
        response = self.client.post(
            reverse("portal:upload_document", args=[other_matter.pk]),
            {"title": "Pièce", "file": "not-a-file"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(other_matter.documents.count(), 0)

    def test_client_can_upload_a_supported_file_to_owned_matter(self):
        self.client.force_login(self.client_user)
        upload = SimpleUploadedFile(
            "piece.pdf", b"%PDF-1.4 test", content_type="application/pdf"
        )
        response = self.client.post(
            reverse("portal:upload_document", args=[self.matter.pk]),
            {"title": "Pièce justificative", "file": upload},
        )
        self.assertRedirects(
            response, reverse("portal:matter_detail", args=[self.matter.pk])
        )
        self.assertEqual(self.matter.documents.count(), 1)
