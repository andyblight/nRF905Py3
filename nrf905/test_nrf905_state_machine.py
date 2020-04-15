#!/usr/bin/env python3

import logging
import unittest

from nrf905.nrf905_state_machine import Nrf905StateMachine

# Set up logging.
#logging.basicConfig(level=logging.ERROR)
logging.basicConfig(level=logging.DEBUG)
# Logger for use in this module.
logger = logging.getLogger('TestNrf905StateMachine')


class TestNrf905StateMachine(unittest.TestCase):

    def setUp(self):
        self.nrf905 = Nrf905Mock()

    # Tear down is not needed.

    def test_graph(self):
        # This is a bit of a hack so uses the machine directly.
        self.nrf905._machine.output_graph()
        # pass

    def test_standby(self):
        logger.debug("\ntest_standby")
        # Put into standby.
        self.assertEqual('power_down', self.nrf905.state)
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        # This call should have no effect.
        self.nrf905.data_ready_function(False)
        self.assertEqual('standby', self.nrf905.state)

    def test_is_busy(self):
        """ Verify that is_busy returns False when in standby and
        power_down states only.
        """
        logger.debug("\ntest_is_busy")
        # Default state is power_down. Expect False
        self.assertEqual('power_down', self.nrf905.state)
        self.assertFalse(self.nrf905._machine.is_busy())
        # Put into standby.
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        self.assertFalse(self.nrf905._machine.is_busy())
        # Try other states
        self.nrf905.transmit("fred")
        self.assertEqual('transmitting_sending', self.nrf905.state)
        self.assertTrue(self.nrf905._machine.is_busy())
        self.nrf905.end_transmit()
        self.assertEqual('standby', self.nrf905.state)
        self.assertFalse(self.nrf905._machine.is_busy())
        self.nrf905.receiver_enabled = True
        self.assertEqual('receiving', self.nrf905.state)
        self.assertTrue(self.nrf905._machine.is_busy())

    def test_transmit(self):
        logger.debug("\ntest_transmit")
        # Basic transmit.
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        # Test waiting
        self.nrf905.transmit("fred")
        self.nrf905.carrier_detect_function(False)
        self.assertEqual('transmitting_waiting', self.nrf905.state)
        # Difficult to simulate changes on different "thread" so send again.
        self.nrf905.transmit("fred")
        self.nrf905.carrier_detect_function(True)
        self.assertEqual('transmitting_sending', self.nrf905.state)
        self.nrf905.data_ready_function(True)
        self.assertEqual('standby', self.nrf905.state)

    def test_retransmit(self):
        logger.debug("\ntest_retransmit")
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        self.nrf905.transmit("bert", 3)
        # No waiting for this.
        self.nrf905.carrier_detect_function(True)
        self.assertEqual('transmitting_sending', self.nrf905.state)
        self.nrf905.data_ready_function(True)
        self.assertEqual('transmitting_sending', self.nrf905.state)
        self.nrf905.data_ready_function(False)
        self.nrf905.data_ready_function(True)
        self.assertEqual('transmitting_sending', self.nrf905.state)
        self.nrf905.data_ready_function(False)
        self.nrf905.data_ready_function(True)
        self.assertEqual('standby', self.nrf905.state)

    def test_receiver_enable(self):
        logger.debug("\ntest_receiver_enable")
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        self.nrf905.receiver_enabled = True
        self.assertEqual('listening', self.nrf905.state)
        self.assertTrue(self.nrf905.receiver_enabled)
        self.nrf905.receiver_enabled = False
        self.assertEqual('standby', self.nrf905.state)
        self.assertFalse(self.nrf905.receiver_enabled)

    def test_receive(self):
        logger.debug("\ntest_receive")
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        self.nrf905.receiver_enabled = True
        self.assertEqual('listening', self.nrf905.state)
        self.nrf905.carrier_detect_function(True)
        self.assertEqual('carrier_busy', self.nrf905.state)
        self.nrf905.address_matched_function(True)
        self.assertEqual('receiving_data', self.nrf905.state)
        self.nrf905.data_ready_function(True)
        self.assertEqual('received', self.nrf905.state)
        # Packet read from registers and posted to queue on exit.
        self.nrf905.address_matched_function(False)
        self.nrf905.data_ready_function(False)
        self.assertEqual('listening', self.nrf905.state)

    def test_receive_to_standby(self):
        logger.debug("\ntest_receive_to_standby")
        self.nrf905.power_up()
        self.assertEqual('standby', self.nrf905.state)
        self.nrf905.receiver_enabled = True
        self.assertEqual('listening', self.nrf905.state)
        self.nrf905.carrier_detect_function(True)
        self.assertEqual('carrier_busy', self.nrf905.state)
        self.nrf905.address_matched_function(True)
        self.assertEqual('receiving_data', self.nrf905.state)
        self.nrf905.data_ready_function(True)
        self.nrf905.receiver_enabled = False
        self.assertEqual('received', self.nrf905.state)
        # Packet read from registers and posted to queue on exit.
        self.nrf905.address_matched_function(False)
        self.nrf905.data_ready_function(False)
        self.assertEqual('standby', self.nrf905.state)


class Nrf905Mock:
    """ Cut down version of the Nrf905 class used for testing the state machine. """
    def __init__(self):
        self._machine = Nrf905StateMachine()
        self._is_rx_enabled = False
        self._retransmit_count = 0
        self._carrier_busy = False

    # These functions simulate those called by the callbacks from pigpio when
    # the GPIO pins changes state.
    def carrier_detect_function(self, value):
        logger.debug("cdf:" + str(value))
        self._carrier_busy = value

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
            if value:
                self._retransmit_count -= 1
                logger.debug("drf: 1")
                if self._retransmit_count <= 0:
                    logger.debug("drf: 1a")
                    self._machine.data_ready_tx()
        elif self._machine.is_receiving():
            logger.debug("drf: 2a")
            if value:
                logger.debug("drf: 2b")
                self._machine.data_ready_rx()
        elif self._machine.is_receiving_received():
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
        elif self._machine.is_receving_listening():
            if not value:
                self._machine.receiver_disable()

    def transmit(self, data, count=1):
        """ Transmit data count times. Default is once. """
        logger.debug("t: sending '" + str(data) + "', " + str(count) + " times")
        self._retransmit_count = count
        # Start transmitting.
        self._machine.transmit()
        # In real program, wait for carrier to be free.
        if not self._carrier_busy:
            self._machine.no_carrier()
        # Post to transmit queue first.
        # Change to transmit state.

    def end_transmit(self):
        """ Fake function for testing.  In reality, the transmit would finish
        after a time, and the data ready callback would then change the state
        to standby.
        """
        self._machine.data_ready_tx()

if __name__ == '__main__':
    unittest.main()
