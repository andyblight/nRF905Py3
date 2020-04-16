#!/usr/bin/env python3

""" Implements the state machine that mimics the external behaviour of the
nRF905 device.  This state machine is driven by a combination of interrupts
from the device, knowledge about configuration register values and user
requests.

Useful info about sub-states here: https://devhub.io/repos/tyarkoni-transitions
"""

import logging

# from transitions.extensions import LockedHierarchicalMachine as Machine
from transitions.extensions import LockedHierarchicalGraphMachine as Machine

# Set up logging; The basic log level will be DEBUG
logging.basicConfig(level=logging.DEBUG)
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.getLogger('transitions').setLevel(logging.INFO)
# Logger for use in this module.
logger = logging.getLogger('Nrf905StateMachine')


class Nrf905StateMachine:
    """ A sub-class of Nrf905 that manages states and transitions.
    The state names were taken from the nRF905 datasheet.
    """
    states = ['sleep', 'standby', {
              'name': 'transmitting', 'initial': 'waiting',
              'children': ['waiting', 'sending']
              }, {
              'name': 'receiving', 'initial': 'listening',
              'children': ['listening', 'receiving_data', 'received']
              }]

    def __init__(self):
        self._machine = Machine(
            model=self, states=self.states, initial='sleep')
        # Add transitions:          (trigger name, previous state, next state)
        # Transmitting
        self._machine.add_transition(
            'transmit', 'standby', 'transmitting')
        self._machine.add_transition(
            'no_carrier', 'transmitting_waiting', 'transmitting_sending')
        self._machine.add_transition(
            'data_ready_tx', 'transmitting_sending', 'standby')
        # Receiving states
        self._machine.add_transition(
            'address_match', 'receiving_listening',
            'receiving_receiving_data')
        self._machine.add_transition(
            'bad_crc', 'receiving_receiving_data', 'receiving_listening')
        self._machine.add_transition(
            'data_ready_rx', 'receiving_receiving_data', 'receiving_received')
        self._machine.add_transition(
            'received2listening', 'receiving_received', 'receiving_listening')
        self._machine.add_transition(
            'received2standby', 'receiving_received', 'standby')
        # Enter/leave receiving
        self._machine.add_transition(
            'receiver_enable', 'standby', 'receiving')
        self._machine.add_transition(
            'receiver_disable', 'receiving', 'standby')
        # Power states
        self._machine.add_transition('power_up', 'sleep', 'standby')
        # This must be last so that the * works.
        self._machine.add_transition(
            'power_down',
            ['standy', 'transmitting', 'receiving'], 'sleep')

    def output_graph(self):
        """ Outputs a graph of the state machine showing all states and
        transitions.
        """
        self._machine.get_graph().draw('nrf905-state-machine.jpg', prog='dot')

    def is_busy(self):
        """ Returns True when in a state that can be interrupted with no loss
        of data.
        """
        busy = True
        state = self.state
        logger.debug("is_busy: " + state)
        if (state == 'sleep' or state == 'standby'
                or state == 'receiving_listening'):
            busy = False
        return busy
