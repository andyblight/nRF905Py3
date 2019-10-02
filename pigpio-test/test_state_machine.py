#!/usr/bin/env python3

""" This file was created so that I could test state machines.
"""
import transitions

class Nrf905StateMachine:
    states = ['power_down', 'standby', 'transmitting', 'carrier_busy',
              'receiving', 'received']
    
    def __init__(self):
        self.machine = transitions.Machine(model=self, states=self.states, initial='power_down')
        # Add transitions:         (trigger name, previous state, next state)
        self.machine.add_transition('power_up', 'power_down', 'standby')
        self.machine.add_transition('transmit', 'standby', 'transmitting', before='write_payload')
        self.machine.add_transition('data_ready_tx', 'transmitting', 'standby')
        self.machine.add_transition('carrier', 'standby', 'carrier_busy')
        self.machine.add_transition('no_carrier', 'carrier_busy', 'standby')
        self.machine.add_transition('address_match', 'carrier_busy', 'receiving')
        self.machine.add_transition('no_address_match', 'receiving', 'standby')
        self.machine.add_transition('data_ready_rx', 'receiving', 'received', before='read_payload')
        self.machine.add_transition('not_data_ready_rx', 'received', 'standby')

    def write_payload(self):
        print("wp")

    def read_payload(self):
        print("rp")


class TestHarness:
    
    def __init__(self):
        self.machine = Nrf905StateMachine()

    def run(self):
        print(self.machine.state)
        self.machine.power_up()
        print(self.machine.state)
        self.machine.transmit()
        print(self.machine.state)
        self.data_ready_callback(True)
        print(self.machine.state)

    def data_ready_callback(self, value):
        print("dr", value)
        if self.machine.is_transmitting():
            if value:
                self.machine.data_ready_tx()
        elif self.machine.is_receiving():
            if value:
                self.machine.data_ready_rx()
            else:
                self.machine.not_data_ready_rx()


##### START HERE ####
print("Tests started")
harness = TestHarness()
harness.run()
print("Tests finished.")
