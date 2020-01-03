#!/usr/bin/env python3

""" Implements the state machine that mimics the behaviour of the nRF905
device.
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
    states = ['power_down', 'standby', 'transmitting', 'retransmitting',
              'listening', 'carrier_busy', 'receiving_data', 'received']

    def __init__(self):
        self._machine = Machine(model=self, states=self.states, initial='power_down')
        # Add transitions:         (trigger name, previous state, next state)
        self._machine.add_transition('power_up', 'power_down', 'standby')
        # Transmit - single shot
        self._machine.add_transition('transmit', 'standby', 'transmitting', before='write_payload')
        self._machine.add_transition('data_ready_tx', 'transmitting', 'standby')
        self._machine.add_transition('retransmit', 'standby', 'retransmitting', before='write_payload')
        self._machine.add_transition('data_ready_tx_re', 'retransmitting', 'standby')
        # Receive
        self._machine.add_transition('receiver_enable', 'standby', 'listening')
        self._machine.add_transition('receiver_disable', 'listening', 'standby')
        self._machine.add_transition('carrier', 'listening', 'carrier_busy')
        self._machine.add_transition('no_carrier', 'carrier_busy', 'listening')
        self._machine.add_transition('address_match', 'carrier_busy', 'receiving_data')
        self._machine.add_transition('no_address_match', 'receiving_data', 'listening')
        self._machine.add_transition('data_ready_rx', 'receiving_data', 'received', before='read_payload')
        # Two possible transitions.
        self._machine.add_transition('received2standby', 'received', 'standby')
        self._machine.add_transition('received2listening', 'received', 'listening')

    def output_graph(self):
        """ Outputs a graph of the state machine showing all states and transitions. """
        self._machine.get_graph().draw('nrf905-state-machine.png', prog='dot')

    def is_busy(self):
        busy = True
        state = self.state
        logger.debug("is_busy: " + state)
        if state == 'power_down' or state == 'standby':
            busy = False
        return busy

    def is_receiving(self):
        receiving = True
        state = self.state
        logger.debug("is_receiving: " + state)
        if state == 'power_down' or state == 'standby':
            receiving = False
        return receiving

    def write_payload(self):
        logger.debug("wp")
        # TODO

    def read_payload(self):
        logger.debug("rp")
        # TODO
