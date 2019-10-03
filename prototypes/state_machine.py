#!/usr/bin/env python3

""" This file was created so that I could test the transitions state machine.
"""
# from transitions.extensions import LockedHierarchicalMachine as Machine
from transitions.extensions import LockedHierarchicalGraphMachine as Machine

class Nrf905StateMachine:
    """ This class will be a sub-calls of Nrf905. """
    states = ['power_down', 'standby', 'listening', 'transmitting', 'transmitting_retran',
              'carrier_busy', 'receiving_data', 'received']
    
    def __init__(self):
        self._machine = Machine(model=self, states=self.states, initial='power_down')
        # Add transitions:         (trigger name, previous state, next state)
        self._machine.add_transition('power_up', 'power_down', 'standby')
        # Transmit - single shot
        self._machine.add_transition('transmit', 'standby', 'transmitting', before='write_payload')
        self._machine.add_transition('data_ready_tx', 'transmitting', 'standby')
        self._machine.add_transition('retransmit', 'standby', 'transmitting_retran', before='write_payload')
        self._machine.add_transition('data_ready_tx_re', 'transmitting_retran', 'standby')
        # Receive
        self._machine.add_transition('trx_ce_hi', 'standby', 'listening')
        self._machine.add_transition('trx_ce_lo', 'listening', 'standby')
        self._machine.add_transition('carrier', 'standby', 'carrier_busy')
        self._machine.add_transition('no_carrier', 'carrier_busy', 'standby')
        self._machine.add_transition('address_match', 'carrier_busy', 'receiving_data')
        self._machine.add_transition('no_address_match', 'receiving_data', 'standby')
        self._machine.add_transition('data_ready_rx', 'receiving_data', 'received', before='read_payload')
        # Two possible transitions.
        self._machine.add_transition('not_data_ready_rx', 'received', 'standby')

    def write_payload(self):
        print("wp")

    def read_payload(self):
        print("rp")
        
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
        print("cdf", value)
        if value:
            self._machine.carrier()
        else:
            self._machine.no_carrier()
            
    def address_matched_function(self, value):
        print("afm", value)
        if value:
            self._machine.address_match()
        else:
            if self._machine.is_receiving_data():
                self._machine.no_address_match()

    def data_ready_function(self, value):
        print("drf", value)
        if self._machine.is_transmitting():
            if value:
                self._machine.data_ready_tx()
        elif self._machine.is_transmitting_retran():
            if value:
                if self._retransmit_count <= 0:
                    self._machine.data_ready_tx_re()
                self._retransmit_count -= 1
        elif self._machine.is_receiving_data():
            if value:
                self._machine.data_ready_rx()
            else:
                # Receive complete
                # Can go into two different states from here.
                if self._is_rx_enabled:
                    self._machine.not_data_ready_rx()
                else:
                    self._machine.not_data_ready_rx()

    # Other functions needed.
    @property
    def state(self):
        return self._machine.state
    
    def power_up(self):
        self._machine.power_up()

    def enable_receiver(self, value):
        if self._machine.is_standby():
            if value:
                self._machine.trx_ce_hi()
                self._is_rx_enabled = True
            else:
                self._machine.trx_ce_lo()
                self._is_rx_enabled = False

    def transmit(self, data):
        """ Transmit data once. """
        print("t: sending", data)
        # Post to transmit queue first.
        self._machine.transmit()

    def retransmit(self, data, count):
        """ Transmit data count times. """
        print("rt: sending", data, count, "times")
        self._retransmit_count = count
        # Post to transmit queue first.
        self._machine.retransmit()

