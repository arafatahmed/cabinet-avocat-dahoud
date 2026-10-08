from django import forms
from django.utils import timezone

from .models import AppointmentRequest, MAX_DOCUMENT_SIZE, PrivateDocument


class ClientMessageForm(forms.Form):
    content = forms.CharField(
        label="Votre message",
        max_length=5000,
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "Écrivez votre message à l'équipe…"}
        ),
    )


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = PrivateDocument
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Ex. Pièce justificative"}),
            "file": forms.ClearableFileInput(attrs={"accept": ".pdf,.doc,.docx,.jpg,.jpeg,.png"}),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if uploaded_file.size > MAX_DOCUMENT_SIZE:
            raise forms.ValidationError("Le fichier ne doit pas dépasser 10 Mo.")
        return uploaded_file


class AppointmentRequestForm(forms.ModelForm):
    preferred_at = forms.DateTimeField(
        label="Date et heure souhaitées",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
        ),
    )

    class Meta:
        model = AppointmentRequest
        fields = ["subject", "preferred_at", "details"]
        widgets = {
            "subject": forms.TextInput(attrs={"placeholder": "Objet du rendez-vous"}),
            "details": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Quelques précisions (facultatif)"}
            ),
        }

    def clean_preferred_at(self):
        preferred_at = self.cleaned_data["preferred_at"]
        if preferred_at <= timezone.now():
            raise forms.ValidationError("Choisissez une date et une heure à venir.")
        return preferred_at
