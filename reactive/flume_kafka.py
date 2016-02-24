from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.flume import Flume
from charms.reactive.helpers import any_file_changed
from jujubigdata.utils import DistConfig


@when('flume-base.installed')
@when_not('flume-sink.joined')
def waiting_for_flume_connection():
    hookenv.status_set('blocked', 'Waiting for connection to Flume sink')


@when('flume-base.installed', 'flume-sink.joined')
@when_not('flume-sink.ready')
def waiting_for_flume_available(sink):  # pylint: disable=unused-argument
    hookenv.status_set('waiting', 'Waiting for Flume sink')


@when('flume-base.installed', 'flume-sink.ready')
def configure_flume(sink):
    hookenv.status_set('maintenance', 'Configuring Flume')
    flume = Flume(DistConfig())
    flume.configure_flume({'agents': sink.agents()})
    if any_file_changed(flume.config_file):
        flume.restart()
    hookenv.status_set('active', 'Ready')
    set_state('flume-kafka.started')


@when('flume-kafka.started')
@when_not('flume-sink.ready')
def stop_flume():
    flume = Flume(DistConfig())
    flume.stop()
    remove_state('flume-kafka.started')
