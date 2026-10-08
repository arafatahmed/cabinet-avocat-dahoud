from django.contrib import admin

from .models import (
    AppointmentRequest,
    CaseUpdate,
    ClientMessage,
    ClientProfile,
    Matter,
    PrivateDocument,
)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone", "created_at")
    search_fields = ("full_name", "user__username", "user__email", "phone")


class CaseUpdateInline(admin.TabularInline):
    model = CaseUpdate
    extra = 0


class PrivateDocumentInline(admin.TabularInline):
    model = PrivateDocument
    extra = 0


class ClientMessageInline(admin.TabularInline):
    model = ClientMessage
    extra = 0


@admin.register(Matter)
class MatterAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "title",
        "client",
        "category",
        "status",
        "next_hearing",
        "updated_at",
    )
    list_filter = ("status", "category")
    search_fields = ("reference", "title", "client__full_name")
    autocomplete_fields = ("client",)
    inlines = (CaseUpdateInline, PrivateDocumentInline, ClientMessageInline)


@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ("client", "subject", "preferred_at", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("client__full_name", "subject")


@admin.register(CaseUpdate)
class CaseUpdateAdmin(admin.ModelAdmin):
    list_display = ("matter", "title", "visible_to_client", "created_at")
    list_filter = ("visible_to_client",)
    search_fields = ("matter__reference", "title", "body")


@admin.register(PrivateDocument)
class PrivateDocumentAdmin(admin.ModelAdmin):
    list_display = ("matter", "title", "visible_to_client", "uploaded_at")
    list_filter = ("visible_to_client",)
    search_fields = ("matter__reference", "title")


@admin.register(ClientMessage)
class ClientMessageAdmin(admin.ModelAdmin):
    list_display = ("matter", "author", "is_from_client", "created_at")
    list_filter = ("is_from_client",)
    search_fields = ("matter__reference", "author__username", "content")
