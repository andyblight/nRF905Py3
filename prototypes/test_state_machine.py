#!/usr/bin/env python3

import unittest

from state_machine import Nrf905Test, Nrf905StateMachine

class TestStateMachine(unittest.TestCase):

    def setUp(self):
        self.nrf905 = Nrf905Test()

    # Tear down is not needed.

    def test_standby(self):
        # Put into standby.
        self.assertEqual('power_down', self.nrf905.state)
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        # This call should have no effect.
        self.nrf905.data_ready_function(False)
        self.assertEqual('standby', self.nrf905.state)

    def test_transmit(self):
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        self.nrf905.transmit("fred")
        print(self.nrf905.state)
        self.nrf905.data_ready_function(True)
        print(self.nrf905.state)

    def test_retransmit(self):
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        self.nrf905.retransmit("bert", 3)
        print(self.nrf905.state)
        self.nrf905.data_ready_function(True)
        print(self.nrf905.state)
        self.nrf905.data_ready_function(False)
        self.nrf905.data_ready_function(True)
        print(self.nrf905.state)
        self.nrf905.data_ready_function(False)
        self.nrf905.data_ready_function(True)
        print(self.nrf905.state)

    def test_receive(self):
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        self.nrf905.carrier_detect_function(True)
        print(self.nrf905.state)
        self.nrf905.address_matched_function(True)
        print(self.nrf905.state)
        self.nrf905.data_ready_function(True)
        print(self.nrf905.state)
        # Packet read from registers and posted to queue on exit. 
        self.nrf905.address_matched_function(False)
        self.nrf905.data_ready_function(False)
        print(self.nrf905.state)
        
    def test_graph(self):
        # This is a bit of a hack so uses the machine directly.
        self.nrf905._machine.output_graph()


if __name__ == '__main__':
    unittest.main()
