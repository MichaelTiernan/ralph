from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ralph.lib.mixins.models import AdminAbsoluteUrlMixin
from ralph.networks.models.networks import IPAddress, NetworkEnvironment


class DHCPEntryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'ethernet', 'ethernet__base_object'
        ).filter(
            hostname__isnull=False,
            dhcp_expose=True,
            ethernet__base_object__isnull=False,
            ethernet__isnull=False,
            ethernet__mac__isnull=False,
        )


class DHCPEntry(IPAddress):
    objects = DHCPEntryManager()

    @property
    def mac(self):
        return self.ethernet and self.ethernet.mac

    class Meta:
        proxy = True


class DHCPServer(AdminAbsoluteUrlMixin, models.Model):
    ip = models.GenericIPAddressField(
        verbose_name=_('IP address'), unique=True
    )
    network_environment = models.ForeignKey(
        NetworkEnvironment, null=True, blank=True
    )
    last_synchronized = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('DHCP Server')
        verbose_name_plural = _('DHCP Servers')

    @classmethod
    def update_last_synchronized(cls, ip, time=None):
        if not time:
            time = timezone.now()
        return cls.objects.filter(ip=ip).update(last_synchronized=time)


class DNSServer(AdminAbsoluteUrlMixin, models.Model):
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP address'),
        unique=True,
    )
    is_default = models.BooleanField(
        verbose_name=_('is default'),
        db_index=True,
        default=False,
    )

    class Meta:
        verbose_name = _('DNS Server')
        verbose_name_plural = _('DNS Servers')

    def __str__(self):
        return '{}'.format(self.ip_address)
