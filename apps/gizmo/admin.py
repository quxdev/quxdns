from django.contrib import admin

from .models import DNSType, Provider, Account, Domain, DNSRecord


@admin.register(DNSType)
class DNSTypeAdmin(admin.ModelAdmin):
    fields = ("id", "name")
    readonly_fields = ("id",)
    list_display = fields


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    fields = ("id", "name", "domain")
    readonly_fields = ("id",)
    list_display = fields


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    fields = ("id", "provider", "user", "login", "api_key")
    readonly_fields = ("id",)
    list_display = fields


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    fields = ("id", "domain", "account")
    readonly_fields = ("id",)
    list_display = fields


@admin.register(DNSRecord)
class DNSRecordAdmin(admin.ModelAdmin):
    fields = (
        "id",
        "domain",
        "name",
        "dns_type",
        "value",
        "ttl",
        "priority",
        "comment",
        "is_active",
    )
    readonly_fields = ("id",)
    list_display = fields
