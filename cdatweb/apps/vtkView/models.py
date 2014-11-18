from django.db import models


class ParaViewHost(models.Model):
    '''
    Defines a host that we can spin up a ParaView instance on.
    '''

    class Meta:
        verbose_name = 'ParaView host'

    HOST_PROTOCOLS = (
        ('http', 'http'),
        ('https', 'https')
    )

    protocol = models.CharField(
        'host protocol',
        max_length=5,
        choices=HOST_PROTOCOLS,
        default='http'
    )

    host = models.URLField(
        'host name or ip address'
    )

    port = models.PositiveIntegerField(
        'host port'
    )
    endpoint = models.URLField(
        'SessionManager endpoint',
        default='/paraview',
        help_text='The endpoint for the paraview launcher.'
    )

    # Possibly a list of applications as ManyToManyField
