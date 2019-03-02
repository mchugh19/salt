# -*- coding: utf-8 -*-
'''
An engine that reads messages from the salt event bus and pushes
them onto a fluent endpoint. 

.. versionadded: neon

:configuration:
All arguments are optional

    Example configuration of default settings

    .. code-block:: yaml

        engines:
          - fluent:
              host: localhost
              port: 24224
              app: engine

    Example fluentd configuration

    .. code-block:: dtd

        <source>
            @type forward
            port 24224
        </source>

        <match saltstack.**>
            @type file
            path /var/log/td-agent/saltstack
        </match>

:depends: fluent-logger
'''

# Import python libraries
from __future__ import absolute_import, print_function, unicode_literals
import logging

# Import salt libs
import salt.utils.event

# Import third-party libs
try:
    from fluent import sender, event
except ImportError:
    handler = None

log = logging.getLogger(__name__)

__virtualname__ = 'fluent'


def __virtual__():
    return __virtualname__ \
        if sender is not None \
        else (False, 'fluent-logger not installed')


def start(host='localhost', port=24224, app='engine'):
    '''
    Listen to salt events and forward them to fluent
    '''

    sender.setup('saltstack', host=host, port=port)

    if __opts__.get('id').endswith('_master'):
        event_bus = salt.utils.event.get_master_event(
                __opts__,
                __opts__['sock_dir'],
                listen=True)
    else:
        event_bus = salt.utils.event.get_event(
            'minion',
            transport=__opts__['transport'],
            opts=__opts__,
            sock_dir=__opts__['sock_dir'],
            listen=True)
    log.info('Fluent engine started')

    while True:
        salt_event = event_bus.get_event_block()
        if salt_event:
            event.Event(app, salt_event)

    sender.close()