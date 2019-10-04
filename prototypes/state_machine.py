#!/usr/bin/env python3

""" This file was created so that I could test the transitions state machine.
"""
import logging

# from transitions.extensions import LockedHierarchicalMachine as Machine
from transitions.extensions import LockedHierarchicalGraphMachine as Machine

# Set up logging; The basic log level will be DEBUG
logging.basicConfig(level=logging.DEBUG)
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.getLogger('transitions').setLevel(logging.INFO)

logger = logging.getLogger('Nrf905StateMachine')

class Nrf905StateMachine:
    """ This class will be a sub-calls of Nrf905. """
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

    def write_payload(self):
        logger.debug("wp")

    def read_payload(self):
        logger.debug("rp")
        
    def output_graph(self):
        self._machine.get_graph().draw('nrf905-state-machine.png', prog='dot')


class Nrf905Test:
    """ Cut down version of the Nrf905 class used for testing the state machine. """
    def __init__(self):
        self._machine = Nrf905StateMachine()
        self._is_rx_enabled = False
        self._retransmit_count = 0

    # These functions simulate those called by the callbacks from pigpio when
    # the GPIO pins changes state.
    def carrier_detect_function(self, value):
        logger.debug("cdf:" + str(value))
        if value:
            self._machine.carrier()
        else:
            self._machine.no_carrier()
            
    def address_matched_function(self, value):
        logger.debug("afm:" + str(value))
        if value:
            self._machine.address_match()
        else:
            if self._machine.is_receiving_data():
                self._machine.no_address_match()

    def data_ready_function(self, value):
        logger.debug("drf:" + str(value) + ", " + str(self._retransmit_count))
        if self._machine.is_transmitting():
            logger.debug("drf: 0")
            if value:
                logger.debug("drf: 0a")
                self._machine.data_ready_tx()
        elif self._machine.is_retransmitting():
            logger.debug("drf: 1")
            if value:
                self._retransmit_count -= 1
                logger.debug("drf: 1a")
                if self._retransmit_count <= 0:
                    logger.debug("drf: 1b")
                    self._machine.data_ready_tx_re()
        elif self._machine.is_receiving_data():
            logger.debug("drf: 2a")
            if value:
                logger.debug("drf: 2b")
                self._machine.data_ready_rx()
        elif self._machine.is_received():
            # Receive complete
            # DR is HI->LO
            logger.debug("drf: 3a")
            if not value:
                # Can go into two different states from here.
                if self._is_rx_enabled:
                    logger.debug("drf: 3b")
                    self._machine.received2listening()
                else:
                    logger.debug("drf: 3c")
                    self._machine.received2standby()

    # Other functions needed.
    @property
    def state(self):
        return self._machine.state
    
    def power_up(self):
        self._machine.power_up()

    @property
    def receiver_enabled(self):
        return self._is_rx_enabled
    
    @receiver_enabled.setter
    def receiver_enabled(self, value):
        logger.debug("er:" + str(value))
        self._is_rx_enabled = value
        if self._machine.is_standby():
            if value:
                self._machine.receiver_enable()
        elif self._machine.is_listening():
            if not value:
                self._machine.receiver_disable()

    def transmit(self, data):
        """ Transmit data once. """
        logger.debug("t:" + str(data))
        # Post to transmit queue first.
        self._machine.transmit()

    def retransmit(self, data, count):
        """ Transmit data count times. """
        logger.debug("rt: sending '" + str(data) + "', " + str(count) + " times")
        self._retransmit_count = count
        # Post to transmit queue first.
        self._machine.retransmit()

