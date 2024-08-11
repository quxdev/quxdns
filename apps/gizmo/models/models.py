import importlib
import inspect

from django.contrib.auth import get_user_model
from django.db import models

from qux.models import QuxModel, default_null_blank

User = get_user_model()


class DNSType(QuxModel):
    """
    A model to store DNS record types.
    Examples: A, AAAA, CNAME, MX, TXT, etc.
    """

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "DNS Type"
        verbose_name_plural = "DNS Types"

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Provider(QuxModel):
    name = models.CharField(max_length=64, unique=True)
    domain = models.CharField(max_length=255, unique=True)

    _cached_providers = {}

    def __repr__(self):
        return self.domain

    def __str__(self):
        return self.name

    def get_provider(self):
        if self.__class__ is not Provider:
            frame = inspect.currentframe().f_back
            caller_method = frame.f_code.co_name
            raise NotImplementedError(f"Provider.{caller_method}() must be overridden")

        if self.name not in self._cached_providers:
            module = importlib.import_module(f"apps.gizmo.models.providers.{self.name}")
            class_name = self.name.capitalize() + "Provider"
            provider_class = getattr(module, class_name)
            self._cached_providers[self.name] = provider_class
        else:
            provider_class = self._cached_providers[self.name]

        return provider_class.objects.get_or_none(pk=self.pk)

    def list_records(self, account=None, domain=None):
        provider = self.get_provider()
        if provider:
            return provider.list_records(account, domain)

        return None

    def create_record(self, account=None, domain=None, record=None):
        provider = self.get_provider()
        if provider:
            return provider.create_record(account, domain, record)

        return None

    def update_record(self, account=None, domain=None, record=None):
        provider = self.get_provider()
        if provider:
            return provider.update_record(account, domain, record)

        return None

    def delete_record(self, account=None, domain=None, record=None):
        provider = self.get_provider()
        if provider:
            return provider.delete_record(account, domain, record)

        return None


class Account(QuxModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="accounts"
    )
    login = models.CharField(max_length=128)
    api_key = models.CharField(
        max_length=255, **default_null_blank, verbose_name="API Key"
    )
    secret_api_key = models.CharField(
        max_length=255, **default_null_blank, verbose_name="Secret API Key"
    )

    class Meta:
        unique_together = ["login", "provider"]

    def __repr__(self):
        return f"{self.login}@{self.provider}"

    def __str__(self):
        return self.__repr__()


class Domain(QuxModel):
    domain = models.CharField(max_length=255, unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __repr__(self):
        return self.domain

    def __str__(self):
        return self.domain

    def list_records(self, account=None):
        if account is None:
            account = self.account
        return self.account.provider.list_records(account, self)


class DNSRecord(QuxModel):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, **default_null_blank)
    dns_type = models.ForeignKey(
        DNSType, on_delete=models.CASCADE, verbose_name="DNS Type"
    )
    value = models.CharField(max_length=255)
    ttl = models.IntegerField(default=600, verbose_name="TTL")
    priority = models.IntegerField(**default_null_blank)
    comment = models.TextField(**default_null_blank)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "DNS Record"
        verbose_name_plural = "DNS Records"
        unique_together = ("domain", "name", "dns_type", "value", "priority")

    def __repr__(self):
        if self.name:
            label = f"{self.name}.{self.domain}"
        else:
            label = self.domain

        return f"{self.dns_type}:{label}"

    def __str__(self):
        return self.__repr__()

    def create_record(self):
        return self.domain.account.provider.create_record(
            self.domain.account, self.domain, self
        )

    def update_record(self):
        return self.domain.account.provider.update_record(
            self.domain.account, self.domain, self
        )

    def delete_record(self):
        return self.domain.account.provider.delete_record(
            self.domain.account, self.domain, self
        )
