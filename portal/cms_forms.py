from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .cms import LANGUAGES, TEXT_FIELDS
from .models import GalleryPhoto, PracticeArea, Publication, SiteSettings, TeamMember


class StaffAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "Cet espace est réservé à l'équipe du cabinet.",
                code="staff_required",
            )


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "telephone",
            "whatsapp",
            "telephone_fixe",
            "email",
            "site_web",
            "adresse",
            "heures",
            "adresse_carte",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stored = self.instance.translations or {}
        self.text_names = {}
        for key, label in TEXT_FIELDS.items():
            self.text_names[key] = {}
            for language_code, language_name in LANGUAGES:
                field_name = f"text_{key}_{language_code}"
                multiline = key.endswith(("p", "bio")) or key in {
                    "c_p1",
                    "c_p2",
                    "s1p",
                    "f_bio",
                    "e_p",
                    "g_p",
                    "ft_desc",
                }
                self.fields[field_name] = forms.CharField(
                    label=f"{label} · {language_name}",
                    required=False,
                    widget=forms.Textarea(attrs={"rows": 3})
                    if multiline
                    else forms.TextInput(),
                )
                self.initial[field_name] = stored.get(key, {}).get(language_code, "")
                self.text_names[key][language_code] = field_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        translations = {}
        for key, language_fields in self.text_names.items():
            values = {
                language: self.cleaned_data[field_name].strip()
                for language, field_name in language_fields.items()
            }
            if any(values.values()):
                translations[key] = values
        instance.translations = translations
        if commit:
            instance.save()
        return instance


class PracticeAreaForm(forms.ModelForm):
    class Meta:
        model = PracticeArea
        fields = [
            "title_fr",
            "title_ar",
            "title_en",
            "description_fr",
            "description_ar",
            "description_en",
            "icon",
            "position",
            "is_active",
        ]
        widgets = {
            "description_fr": forms.Textarea(attrs={"rows": 3}),
            "description_ar": forms.Textarea(attrs={"rows": 3, "dir": "rtl"}),
            "description_en": forms.Textarea(attrs={"rows": 3}),
        }


class GalleryPhotoForm(forms.ModelForm):
    class Meta:
        model = GalleryPhoto
        fields = [
            "image_url",
            "caption_fr",
            "caption_ar",
            "caption_en",
            "position",
            "is_slide",
            "is_active",
        ]
        widgets = {
            "caption_ar": forms.TextInput(attrs={"dir": "rtl"}),
        }

    def clean_image_url(self):
        url = self.cleaned_data["image_url"]
        if not (
            url.lower().startswith("https://")
            or (
                url.startswith("/static/images/")
                and ".." not in url
                and "\\" not in url
            )
        ):
            raise forms.ValidationError(
                "Utilisez une URL HTTPS ou un chemin d'image du site."
            )
        return url


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            "name_fr", "name_ar", "name_en",
            "title_fr", "title_ar", "title_en",
            "bio_fr", "bio_ar", "bio_en",
            "credentials_fr", "credentials_ar", "credentials_en",
            "portrait_url", "position", "is_active",
        ]
        widgets = {
            "name_ar": forms.TextInput(attrs={"dir": "rtl"}),
            "title_ar": forms.TextInput(attrs={"dir": "rtl"}),
            "bio_fr": forms.Textarea(attrs={"rows": 3}),
            "bio_ar": forms.Textarea(attrs={"rows": 3, "dir": "rtl"}),
            "bio_en": forms.Textarea(attrs={"rows": 3}),
            "credentials_fr": forms.Textarea(attrs={"rows": 2}),
            "credentials_ar": forms.Textarea(attrs={"rows": 2, "dir": "rtl"}),
            "credentials_en": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        for language in ("fr", "ar", "en"):
            key = f"credentials_{language}"
            value = cleaned.get(key)
            if isinstance(value, str):
                cleaned[key] = [
                    line.strip() for line in value.splitlines() if line.strip()
                ]
        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for language in ("fr", "ar", "en"):
            name = f"credentials_{language}"
            self.fields[name] = forms.CharField(
                label=self.fields[name].label,
                required=False,
                widget=forms.Textarea(
                    attrs={"rows": 2, "dir": "rtl"}
                    if language == "ar"
                    else {"rows": 2}
                ),
                initial="\n".join(self.instance.__dict__.get(name) or []),
            )


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = [
            "category_fr", "category_ar", "category_en",
            "title_fr", "title_ar", "title_en",
            "excerpt_fr", "excerpt_ar", "excerpt_en",
            "published_at", "position", "is_active",
        ]
        widgets = {
            "category_ar": forms.TextInput(attrs={"dir": "rtl"}),
            "title_ar": forms.TextInput(attrs={"dir": "rtl"}),
            "excerpt_fr": forms.Textarea(attrs={"rows": 3}),
            "excerpt_ar": forms.Textarea(attrs={"rows": 3, "dir": "rtl"}),
            "excerpt_en": forms.Textarea(attrs={"rows": 3}),
            "published_at": forms.DateInput(attrs={"type": "date"}),
        }
