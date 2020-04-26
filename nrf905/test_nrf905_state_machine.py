#!/usr/bin/env python3
""" Test harness.
Could do with some improvements so that it is easier to match to the
flow charts in the datasheet, in particular adding mock functions
to set the pin states, TRX_CE etc.
"""

import logging
import unittest

from nrf905.nrf905_state_machine import Nrf905StateMachine

# Set up logging.
# logging.basicConfig(level=logging.ERROR)
logging.basicConfig(level=logging.DEBUG)
# Logger for use in this module.
logger = logging.getLogger("TestNrf905StateMachine")


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
        self.assertEqual("sleep", self.nrf905.state)
        self.nrf905.power_up()
        self.assertEqual("standby", self.nrf905.state)
        # This call should have no effect.
        self.nrf905.data_ready_function(False)
        self.assertEqual("standby", self.nrf905.state)

    def test_is_busy(self):
        """ Verify that is_busy returns False when in standby and
        sleep states only.
        """
        logger.debug("\ntest_is_busy")
        # Default state is sleep. Expect False
        self.assertEqual("sleep", self.nrf905.state)
        self.assertFalse(self.nrf905._machine.is_busy())
        # Put into standby.
        self.nrf905.power_up()
        self.assertEqual("standby", self.nrf905.state)
        self.assertFalse(self.nrf905._machine.is_busy())
        # Try other states
        self.nrf905.transmit("fred")
        self.assertEqual("transmitting_sending", self.nrf905.state)
        self.assertTrue(self.nrf905._machine.is_busy())
        self.nrf905.end_transmit()
        self.assertEqual("standby", self.nrf905.state)
        self.assertFalse(self.nrf905._machine.is_busy())
        self.nrf905.receiver_enabled = True
        self.assertEqual("receiving_listening", self.nrf905.state)
        self.assertFalse(self.nrf905._machine.is_busy())

    def test_transmit_waiting(self):
        logger.debug("\ntest_transmit_waiting")
        self.nrf905.power_up()
        self.assertEqual("standby", self.nrf905.state)
        # Test waiting send.
        self.nrf905.carrier_detect_function(True)
        self.nrf905.transmit("fred")
        self.assertEqual("transmitting_waiting", self.nrf905.state)
        self.nrf905.carrier_detect_function(False)
        self.assertEqual("transmitting_sending", self.nrf905.state)
        self.nrf905.data_ready_function(True)
        self.assertEqual("standby", self.nrf905.state)

    def test_transmit_no_wait(self):
        logger.debug("\ntest_transmit_no_wait")
        self.nrf905.power_up()
        self.assertEqual("standby", self.nrf905.state)
        # Test immediate send (carrier not busy).
        self.nrf905.carrier_detect_function(False)
        self.nrf905.transmit("bert")
        self.assertEqual("transmitting_sending", self.nrf905.state)
        self.nrf905.data_ready_function(True)
        self.assertEqual("standby", self.nrf905.state)

    def test_receiver_enable(self):
        logger.debug("\ntest_receiver_enable")
        self.nrf905.power_up()
        self.assertEqual("standby", self.nrf905.state)
        self.nrf905.receiver_enabled = True
        self.assertEqual("receiving_listening", self.nrf905.state)
        self.assertTrue(self.nrf905.receiver_enabled)
        self.nrf905.receiver_enabled = False
        self.assertEqual("standby", self.nrf905.state)
        self.assertFalse(self.nrf905.receiver_enabled)

    def test_receive(self):
        logger.debug("\ntest_receive")
        self.nrf905.power_up()
        self.assertEqual("standby", self.nrf905.state)
        self.nrf905.receiver_enabled = True
        self.assertEqual("receiving_listening", self.nrf905.state)
        self.nrf905.carrier_detect_function(True)
        self.nrf905.address_matched_function(True)
        self.assertEqual("receiving_receiving_data", self.nrf905.state)
        self.nrf905.data_ready_function(True)
        self.assertEqual("receiving_received", self.nrf905.state)
        # Packet read from SPI registers.
        self.nrf905.address_matched_function(False)
        self.nrf905.data_ready_function(False)
        self.assertEqual("receiving_listening", self.nrf905.state)

    def test_receive_to_standby(self):
        logger.debug("\ntest_receive_to_standby")
        self.nrf905.power_up()
        self.assertEqual("standby", self.nrf905.state)
        self.nrf905.receiver_enabled = True
        self.assertEqual("receiving_listening", self.nrf905.state)
        self.nrf905.carrier_detect_function(True)
        self.nrf905.address_matched_function(True)
        self.assertEqual("receiving_receiving_data", self.nrf905.state)
        self.nrf905.data_ready_function(True)
        self.assertEqual("receiving_received", self.nrf905.state)
        self.nrf905.receiver_enabled = False
        # Packet read from SPI registers.
        self.nrf905.address_matched_function(False)
        self.nrf905.data_ready_function(False)
        self.assertEqual("standby", self.nrf905.state)


class Nrf905Mock:
    """ Cut down version of the Nrf905 class used for testing the state
    machine.
    """

    def __init__(self):
        self._machine = Nrf905StateMachine()
        self._is_rx_enabled = False
        self._retransmit_count = 0
        self._carrier_busy = False

    # These functions simulate those called by the callbacks from pigpio when
    # the GPIO pins changes state.
    def carrier_detect_function(self, high):
        logger.debug("cdf:" + str(high))
        self._carrier_busy = high
        if not high:
            if self._machine.is_transmitting_waiting():
                self._machine.no_carrier()

    def address_matched_function(self, high):
        logger.debug("afm:" + str(high))
        if high:
            if self._machine.is_receiving_listening():
                self._machine.address_match()
        else:
            if self._machine.is_receiving_receiving_data():
                self._machine.bad_crc()

    def data_ready_function(self, high):
        logger.debug("drf:" + str(high))
        if high:
            if self._machine.is_transmitting_sending():
                # Transmit has completed.
                # We don't do retransmits so always go to standby.
                logger.debug("drf: tx")
                self._machine.data_ready_tx()
            elif self._machine.is_receiving_receiving_data():
                # Successful receive with good CRC (if enabled).
                logger.debug("drf: rx")
                self._machine.data_ready_rx()
        else:
            # Hi to lo
            if self._machine.is_receiving_received():
                # This happens when the data has been read from the
                # payload registers.
                self._machine.received2listening()

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
    def receiver_enabled(self, high):
        logger.debug("er:" + str(high))
        self._is_rx_enabled = high
        if high:
            # Lo to hi.
            self._machine.receiver_enable()
        else:
            # Hi to lo.
            self._machine.receiver_disable()

    def transmit(self, data):
        """ Transmit data. """
        logger.debug("t: sending '" + str(data))
        # Write payload (data) to device.
        # Start transmitting (TRX_CE goes hi).
        if self._carrier_busy:
            # This puts it into transmitting_waiting.
            self._machine.transmit_wait()
        else:
            # Go straight into sending.
            self._machine.transmit_now()

    def end_transmit(self):
        """ Fake function for testing.  In reality, the transmit would finish
        after a time, and the data ready callback would then change the state
        to standby.
        """
        self._machine.data_ready_tx()


if __name__ == "__main__":
    unittest.main()
