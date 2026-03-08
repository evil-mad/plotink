"""
Tests for ebb3_serial.py

part of https://github.com/evil-mad/plotink

"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock

from plotink import ebb3_serial


# python -m unittest discover in top-level package dir


def make_mock_port(responses):
    """
    Create a mock serial port that returns the given byte responses
    in sequence from readline(). Each entry in `responses` should be
    a bytes object (e.g. b'EBBv13_and_above ...\\r\\n').
    """
    port = MagicMock()
    port.readline = MagicMock(side_effect=responses)
    return port


class ParseVersionTestCase(unittest.TestCase):
    """Tests for EBB3.parse_version() — pure logic, no serial I/O."""

    def test_normal_version_string(self):
        ebb = ebb3_serial.EBB3()
        ebb.parse_version("EBBv13_and_above EB Firmware Version 3.0.2")
        self.assertEqual(ebb.version, "3.0.2")
        self.assertIsNotNone(ebb.version_parsed)

    def test_version_with_extra_whitespace(self):
        ebb = ebb3_serial.EBB3()
        ebb.parse_version("EBBv13_and_above EB Firmware Version 3.1.0  \r\n")
        self.assertEqual(ebb.version, "3.1.0")

    def test_garbage_string_no_version(self):
        ebb = ebb3_serial.EBB3()
        ebb.parse_version("some random garbage")
        self.assertIsNone(ebb.version)
        self.assertIsNone(ebb.version_parsed)

    def test_empty_string(self):
        ebb = ebb3_serial.EBB3()
        ebb.parse_version("")
        self.assertIsNone(ebb.version)


class MinVersionTestCase(unittest.TestCase):
    """Tests for EBB3.min_version()."""

    def setUp(self):
        self.ebb = ebb3_serial.EBB3()
        self.ebb.parse_version("EBBv13_and_above EB Firmware Version 3.0.2")

    def test_equal_version(self):
        self.assertTrue(self.ebb.min_version("3.0.2"))

    def test_lower_version(self):
        self.assertTrue(self.ebb.min_version("3.0.1"))

    def test_higher_version(self):
        self.assertFalse(self.ebb.min_version("3.1.0"))

    def test_invalid_version_string(self):
        self.assertIsNone(self.ebb.min_version("not_a_version"))

    def test_unparsed_device_version(self):
        """min_version returns None when device version is unknown."""
        ebb = ebb3_serial.EBB3()  # version_parsed is None
        self.assertIsNone(ebb.min_version("3.0.2"))


class FindFirstTestCase(unittest.TestCase):
    """Tests for EBB3.find_first() with mocked comports."""

    @patch('plotink.ebb3_serial.comports')
    def test_find_by_name(self, mock_comports):
        mock_comports.return_value = [
            ('/dev/ttyUSB0', 'EiBotBoard', 'USB VID:PID=04D8:FD92'),
        ]
        ebb = ebb3_serial.EBB3()
        ebb.find_first()
        self.assertEqual(ebb.port_name, '/dev/ttyUSB0')

    @patch('plotink.ebb3_serial.comports')
    def test_find_by_vid_pid(self, mock_comports):
        mock_comports.return_value = [
            ('/dev/ttyUSB0', 'Some Other Device', 'USB VID:PID=04D8:FD92 SER=ABC'),
        ]
        ebb = ebb3_serial.EBB3()
        ebb.find_first()
        self.assertEqual(ebb.port_name, '/dev/ttyUSB0')

    @patch('plotink.ebb3_serial.comports')
    def test_no_ebb_found(self, mock_comports):
        mock_comports.return_value = [
            ('/dev/ttyUSB0', 'Arduino Uno', 'USB VID:PID=1234:5678'),
        ]
        ebb = ebb3_serial.EBB3()
        ebb.find_first()
        self.assertIsNone(ebb.port_name)

    @patch('plotink.ebb3_serial.comports')
    def test_empty_port_list(self, mock_comports):
        mock_comports.return_value = []
        ebb = ebb3_serial.EBB3()
        ebb.find_first()
        self.assertIsNone(ebb.port_name)

    @patch('plotink.ebb3_serial.comports')
    def test_comports_type_error(self, mock_comports):
        mock_comports.side_effect = TypeError
        ebb = ebb3_serial.EBB3()
        ebb.find_first()
        self.assertIsNone(ebb.port_name)


class ConnectTestCase(unittest.TestCase):
    """Tests for EBB3.connect() with mocked serial port.

    connect() calls _get_port_name() which calls find_first(), so we must
    mock comports to return an EBB port in addition to mocking serial.Serial.
    """

    VERSION_RESPONSE = b'EBBv13_and_above EB Firmware Version 3.0.2\r\n'
    FUTURE_SYNTAX_RESPONSE = b'CU,10,1\r\n'
    NICKNAME_RESPONSE = b'QT,MyEBB\r\n'

    EBB_PORT = ('/dev/ttyUSB0', 'EiBotBoard', 'USB VID:PID=04D8:FD92')

    @patch('plotink.ebb3_serial.comports')
    @patch('plotink.ebb3_serial.serial.Serial')
    def test_successful_connect(self, mock_serial_cls, mock_comports):
        mock_comports.return_value = [self.EBB_PORT]
        mock_port = make_mock_port([
            self.VERSION_RESPONSE,      # version query
            self.FUTURE_SYNTAX_RESPONSE, # CU,10,1
            self.NICKNAME_RESPONSE,      # QT query
        ])
        mock_serial_cls.return_value = mock_port

        ebb = ebb3_serial.EBB3()
        result = ebb.connect()

        self.assertTrue(result)
        self.assertIsNone(ebb.err)
        self.assertEqual(ebb.version, '3.0.2')
        self.assertEqual(ebb.name, 'MyEBB')

    @patch('plotink.ebb3_serial.comports')
    @patch('plotink.ebb3_serial.serial.Serial')
    def test_connect_garbled_first_response_then_retry(self, mock_serial_cls, mock_comports):
        """First version response is garbled, second succeeds."""
        mock_comports.return_value = [self.EBB_PORT]
        mock_port = make_mock_port([
            b'garbled nonsense\r\n',     # first try fails
            self.VERSION_RESPONSE,       # second try succeeds
            self.FUTURE_SYNTAX_RESPONSE,
            self.NICKNAME_RESPONSE,
        ])
        mock_serial_cls.return_value = mock_port

        ebb = ebb3_serial.EBB3()
        result = ebb.connect()

        self.assertTrue(result)
        self.assertIsNone(ebb.err)
        self.assertEqual(ebb.version, '3.0.2')

    @patch('plotink.ebb3_serial.comports')
    @patch('plotink.ebb3_serial.serial.Serial')
    def test_connect_non_ascii_bytes_handled(self, mock_serial_cls, mock_comports):
        """Non-ASCII bytes before 'Firmware Version' — EBB found, version parses OK.
        The 0xc0 is in the prefix portion that gets split away by parse_version."""
        mock_comports.return_value = [self.EBB_PORT]
        garbled = b'EBBv13_and_above\xc0EB Firmware Version 3.0.2\r\n'
        mock_port = make_mock_port([
            garbled,                     # first try: has EBB, version parseable
            self.FUTURE_SYNTAX_RESPONSE,
            self.NICKNAME_RESPONSE,
        ])
        mock_serial_cls.return_value = mock_port

        ebb = ebb3_serial.EBB3()
        result = ebb.connect()

        self.assertTrue(result)
        self.assertIsNone(ebb.err)
        self.assertEqual(ebb.version, '3.0.2')

    @patch('plotink.ebb3_serial.comports')
    @patch('plotink.ebb3_serial.serial.Serial')
    def test_connect_non_ascii_no_ebb_marker(self, mock_serial_cls, mock_comports):
        """Non-ASCII bytes without EBB marker on first try; retry succeeds."""
        mock_comports.return_value = [self.EBB_PORT]
        garbled = b'\xc0\xc1\xc2 no marker here\r\n'
        mock_port = make_mock_port([
            garbled,                     # first try fails (no "EBB")
            self.VERSION_RESPONSE,       # retry succeeds
            self.FUTURE_SYNTAX_RESPONSE,
            self.NICKNAME_RESPONSE,
        ])
        mock_serial_cls.return_value = mock_port

        ebb = ebb3_serial.EBB3()
        result = ebb.connect()

        self.assertTrue(result)
        self.assertIsNone(ebb.err)

    @patch('plotink.ebb3_serial.comports')
    @patch('plotink.ebb3_serial.serial.Serial')
    def test_connect_non_ascii_both_attempts(self, mock_serial_cls, mock_comports):
        """Non-ASCII in both attempts without EBB marker — connect fails gracefully."""
        mock_comports.return_value = [self.EBB_PORT]
        garbled = b'\xc0\xc1\xc2\r\n'
        mock_port = make_mock_port([
            garbled,
            garbled,
        ])
        mock_serial_cls.return_value = mock_port

        ebb = ebb3_serial.EBB3()
        result = ebb.connect()

        self.assertFalse(result)
        self.assertIsNotNone(ebb.err)

    @patch('plotink.ebb3_serial.comports')
    @patch('plotink.ebb3_serial.serial.Serial')
    def test_connect_empty_responses(self, mock_serial_cls, mock_comports):
        """Empty responses from both version queries — connect fails."""
        mock_comports.return_value = [self.EBB_PORT]
        mock_port = make_mock_port([
            b'\r\n',
            b'\r\n',
        ])
        mock_serial_cls.return_value = mock_port

        ebb = ebb3_serial.EBB3()
        result = ebb.connect()

        self.assertFalse(result)
        self.assertIsNotNone(ebb.err)

    @patch('plotink.ebb3_serial.comports')
    @patch('plotink.ebb3_serial.serial.Serial')
    def test_connect_serial_exception(self, mock_serial_cls, mock_comports):
        mock_comports.return_value = [self.EBB_PORT]
        mock_serial_cls.side_effect = ebb3_serial.serial.SerialException("port error")

        ebb = ebb3_serial.EBB3()
        result = ebb.connect()

        self.assertFalse(result)
        self.assertIsNotNone(ebb.err)

    @patch('plotink.ebb3_serial.comports')
    @patch('plotink.ebb3_serial.serial.Serial')
    def test_connect_firmware_too_old(self, mock_serial_cls, mock_comports):
        mock_comports.return_value = [self.EBB_PORT]
        old_fw = b'EBBv13_and_above EB Firmware Version 2.9.0\r\n'
        mock_port = make_mock_port([old_fw])
        mock_serial_cls.return_value = mock_port

        ebb = ebb3_serial.EBB3()
        result = ebb.connect()

        self.assertFalse(result)
        self.assertIn("not supported", ebb.err)

    def test_connect_already_connected(self):
        ebb = ebb3_serial.EBB3()
        ebb.port = MagicMock()  # Already has a port
        result = ebb.connect()
        self.assertTrue(result)

    @patch('plotink.ebb3_serial.comports')
    def test_connect_no_port_found(self, mock_comports):
        mock_comports.return_value = []
        ebb = ebb3_serial.EBB3()
        result = ebb.connect()
        self.assertFalse(result)
        self.assertIsNotNone(ebb.err)


class CommandTestCase(unittest.TestCase):
    """Tests for EBB3.command()."""

    def _make_connected_ebb(self, responses):
        ebb = ebb3_serial.EBB3()
        ebb.port = make_mock_port(responses)
        return ebb

    def test_successful_command(self):
        ebb = self._make_connected_ebb([b'SM,OK\r\n'])
        result = ebb.command('SM,1000,500,0')
        self.assertTrue(result)
        self.assertIsNone(ebb.err)

    def test_command_with_error_response(self):
        ebb = self._make_connected_ebb([b'SM,Err: bad value\r\n'])
        result = ebb.command('SM,1000,500,0')
        self.assertFalse(result)
        self.assertIn("Error reported by EBB", ebb.err)

    def test_command_unexpected_response(self):
        ebb = self._make_connected_ebb([b'XX,something\r\n'])
        result = ebb.command('SM,1000,500,0')
        self.assertFalse(result)
        self.assertIn("Unexpected response", ebb.err)

    def test_command_timeout_empty_responses(self):
        """26 empty responses exhaust retries, producing a timeout error."""
        ebb = self._make_connected_ebb([b'\r\n'] * 26)
        result = ebb.command('SM,1000,500,0')
        self.assertFalse(result)
        self.assertIn("Timeout", ebb.err)

    def test_command_non_ascii_in_response(self):
        """Non-ASCII bytes don't crash — they produce an unexpected response error."""
        ebb = self._make_connected_ebb([b'SM,\xc0\xc1\r\n'])
        result = ebb.command('SM,1000,500,0')
        # Should not raise UnicodeDecodeError; may record error about unexpected response
        self.assertIsInstance(result, bool)

    def test_command_no_port(self):
        ebb = ebb3_serial.EBB3()
        result = ebb.command('SM,1000,500,0')
        self.assertFalse(result)

    def test_command_existing_error(self):
        ebb = ebb3_serial.EBB3()
        ebb.port = MagicMock()
        ebb.err = "previous error"
        result = ebb.command('SM,1000,500,0')
        self.assertFalse(result)

    def test_command_single_letter(self):
        ebb = self._make_connected_ebb([b'v,EBBv13...\r\n'])
        result = ebb.command('v')
        self.assertTrue(result)

    def test_command_single_letter_with_args(self):
        ebb = self._make_connected_ebb([b'S,OK\r\n'])
        result = ebb.command('S,1')
        self.assertTrue(result)


class QueryTestCase(unittest.TestCase):
    """Tests for EBB3.query()."""

    def _make_connected_ebb(self, responses):
        ebb = ebb3_serial.EBB3()
        ebb.port = make_mock_port(responses)
        return ebb

    def test_successful_query(self):
        ebb = self._make_connected_ebb([b'QC,1234,5678\r\n'])
        result = ebb.query('QC')
        self.assertEqual(result, '1234,5678')

    def test_query_strips_command_prefix(self):
        ebb = self._make_connected_ebb([b'QT,MyEBB\r\n'])
        result = ebb.query('QT')
        self.assertEqual(result, 'MyEBB')

    def test_query_error_response(self):
        ebb = self._make_connected_ebb([b'QC,Err: bad\r\n'])
        result = ebb.query('QC')
        self.assertIsNone(result)
        self.assertIsNotNone(ebb.err)

    def test_query_unexpected_response(self):
        ebb = self._make_connected_ebb([b'XX,something\r\n'])
        result = ebb.query('QC')
        self.assertIsNone(result)
        self.assertIsNotNone(ebb.err)

    def test_query_timeout(self):
        ebb = self._make_connected_ebb([b'\r\n'] * 26)
        result = ebb.query('QC')
        self.assertIsNone(result)

    def test_query_non_ascii_in_response(self):
        ebb = self._make_connected_ebb([b'QC,\xc0\xc1\r\n'])
        result = ebb.query('QC')
        # Should not raise; garbled response won't match expected prefix
        # (replacement chars may or may not match depending on query)

    def test_query_no_port(self):
        ebb = ebb3_serial.EBB3()
        result = ebb.query('QC')
        self.assertIsNone(result)

    def test_query_single_letter(self):
        ebb = self._make_connected_ebb([b'v,EBBv13...\r\n'])
        result = ebb.query('v')
        self.assertEqual(result, 'EBBv13...')


class QueryStatusbyteTestCase(unittest.TestCase):
    """Tests for EBB3.query_statusbyte()."""

    def _make_connected_ebb(self, responses):
        ebb = ebb3_serial.EBB3()
        ebb.port = make_mock_port(responses)
        return ebb

    def test_normal_statusbyte(self):
        ebb = self._make_connected_ebb([b'QG,3E\r\n'])
        result = ebb.query_statusbyte()
        self.assertEqual(result, 0x3E)

    def test_statusbyte_zero(self):
        ebb = self._make_connected_ebb([b'QG,00\r\n'])
        result = ebb.query_statusbyte()
        self.assertEqual(result, 0)

    def test_statusbyte_ff(self):
        ebb = self._make_connected_ebb([b'QG,FF\r\n'])
        result = ebb.query_statusbyte()
        self.assertEqual(result, 0xFF)

    def test_statusbyte_unexpected_response(self):
        """Unexpected response records an error but doesn't return early;
        falls through to int() parse. 'XX,3E'[3:] = '3E' -> 62."""
        ebb = self._make_connected_ebb([b'XX,3E\r\n'])
        result = ebb.query_statusbyte()
        self.assertIsNotNone(ebb.err)
        # Note: code records error but still parses the hex suffix
        self.assertEqual(result, 0x3E)

    def test_statusbyte_error_response(self):
        ebb = self._make_connected_ebb([b'QG,Err: bad\r\n'])
        result = ebb.query_statusbyte()
        self.assertIsNone(result)

    def test_statusbyte_non_ascii(self):
        ebb = self._make_connected_ebb([b'QG,\xc0\xc1\r\n'])
        result = ebb.query_statusbyte()
        # Should not raise; replacement chars won't parse as hex
        self.assertIsNone(result)

    def test_statusbyte_no_port(self):
        ebb = ebb3_serial.EBB3()
        result = ebb.query_statusbyte()
        self.assertIsNone(result)


class DisconnectTestCase(unittest.TestCase):
    """Tests for EBB3.disconnect()."""

    def test_disconnect_closes_port(self):
        ebb = ebb3_serial.EBB3()
        mock_port = MagicMock()
        ebb.port = mock_port
        ebb.disconnect()
        mock_port.close.assert_called_once()
        self.assertIsNone(ebb.port)

    def test_disconnect_no_port(self):
        ebb = ebb3_serial.EBB3()
        ebb.disconnect()  # Should not raise
        self.assertIsNone(ebb.port)

    def test_disconnect_close_raises(self):
        ebb = ebb3_serial.EBB3()
        mock_port = MagicMock()
        mock_port.close.side_effect = ebb3_serial.serial.SerialException
        ebb.port = mock_port
        ebb.disconnect()  # Should not raise
        self.assertIsNone(ebb.port)


class RebootBootloadTestCase(unittest.TestCase):
    """Tests for EBB3.reboot() and bootload()."""

    def test_reboot_success(self):
        ebb = ebb3_serial.EBB3()
        ebb.port = MagicMock()
        result = ebb.reboot()
        self.assertTrue(result)
        self.assertIsNone(ebb.port)

    def test_reboot_no_port(self):
        ebb = ebb3_serial.EBB3()
        result = ebb.reboot()
        self.assertFalse(result)

    def test_reboot_with_error(self):
        ebb = ebb3_serial.EBB3()
        ebb.port = MagicMock()
        ebb.err = "some error"
        result = ebb.reboot()
        self.assertFalse(result)

    def test_bootload_success(self):
        ebb = ebb3_serial.EBB3()
        ebb.port = MagicMock()
        result = ebb.bootload()
        self.assertTrue(result)
        self.assertIsNone(ebb.port)

    def test_bootload_flushes_before_close(self):
        """Verify flush() is called before disconnect() so the BL command
        is fully transmitted over USB before the port is closed."""
        ebb = ebb3_serial.EBB3()
        mock_port = MagicMock()
        call_order = []
        mock_port.flush.side_effect = lambda: call_order.append('flush')
        mock_port.close.side_effect = lambda: call_order.append('close')
        ebb.port = mock_port
        result = ebb.bootload()
        self.assertTrue(result)
        self.assertEqual(call_order, ['flush', 'close'])

    def test_bootload_no_port(self):
        ebb = ebb3_serial.EBB3()
        result = ebb.bootload()
        self.assertFalse(result)


class NicknameTestCase(unittest.TestCase):
    """Tests for EBB3.query_nickname() and write_nickname()."""

    def test_query_nickname(self):
        ebb = ebb3_serial.EBB3()
        ebb.port = make_mock_port([b'QT,MyPlotter\r\n'])
        ebb.query_nickname()
        self.assertEqual(ebb.name, 'MyPlotter')

    def test_query_nickname_whitespace_only(self):
        """QT response with only spaces after prefix: query() strips prefix+comma,
        leaving empty string after strip(). Empty string is not whitespace-only,
        so name is set to empty string."""
        ebb = ebb3_serial.EBB3()
        ebb.port = make_mock_port([b'QT,   \r\n'])
        ebb.query_nickname()
        self.assertEqual(ebb.name, '')

    def test_query_nickname_no_port(self):
        ebb = ebb3_serial.EBB3()
        ebb.query_nickname()
        self.assertIsNone(ebb.name)

    def test_write_nickname(self):
        ebb = ebb3_serial.EBB3()
        ebb.port = make_mock_port([b'ST,OK\r\n'])
        result = ebb.write_nickname('TestName')
        self.assertTrue(result)
        self.assertEqual(ebb.name, 'TestName')

    def test_write_nickname_empty_clears(self):
        ebb = ebb3_serial.EBB3()
        ebb.port = make_mock_port([b'ST,OK\r\n'])
        result = ebb.write_nickname('   ')
        self.assertTrue(result)
        self.assertEqual(ebb.name, '')


class VarReadWriteTestCase(unittest.TestCase):
    """Tests for EBB3.var_write/read and int32 variants."""

    def _make_connected_ebb(self, responses):
        ebb = ebb3_serial.EBB3()
        ebb.port = make_mock_port(responses)
        return ebb

    def test_var_write(self):
        ebb = self._make_connected_ebb([b'SL,OK\r\n'])
        result = ebb.var_write(42, 0)
        self.assertTrue(result)

    def test_var_read(self):
        ebb = self._make_connected_ebb([b'QL,42\r\n'])
        result = ebb.var_read(0)
        self.assertEqual(result, 42)

    def test_var_write_int32(self):
        # 4 SL commands, each returns OK
        ebb = self._make_connected_ebb([b'SL,OK\r\n'] * 4)
        result = ebb.var_write_int32(12345, 0)
        self.assertTrue(result)

    def test_var_read_int32(self):
        # Value 12345 = 0x00003039 -> bytes [0, 0, 48, 57]
        ebb = self._make_connected_ebb([
            b'QL,0\r\n',
            b'QL,0\r\n',
            b'QL,48\r\n',
            b'QL,57\r\n',
        ])
        result = ebb.var_read_int32(0)
        self.assertEqual(result, 12345)

    def test_var_write_int32_negative(self):
        ebb = self._make_connected_ebb([b'SL,OK\r\n'] * 4)
        result = ebb.var_write_int32(-1, 0)
        self.assertTrue(result)

    def test_var_read_int32_negative(self):
        # -1 = 0xFFFFFFFF -> bytes [255, 255, 255, 255]
        ebb = self._make_connected_ebb([
            b'QL,255\r\n',
            b'QL,255\r\n',
            b'QL,255\r\n',
            b'QL,255\r\n',
        ])
        result = ebb.var_read_int32(0)
        self.assertEqual(result, -1)


class ListEbbPortsTestCase(unittest.TestCase):
    """Tests for module-level list_ebb_ports()."""

    @patch('plotink.ebb3_serial.comports')
    def test_finds_ebb_by_name(self, mock_comports):
        mock_comports.return_value = [
            ('/dev/ttyUSB0', 'EiBotBoard', 'USB VID:PID=04D8:FD92'),
        ]
        result = ebb3_serial.list_ebb_ports()
        self.assertEqual(len(result), 1)

    @patch('plotink.ebb3_serial.comports')
    def test_no_ebbs(self, mock_comports):
        mock_comports.return_value = [
            ('/dev/ttyUSB0', 'Arduino', 'USB VID:PID=1234:5678'),
        ]
        result = ebb3_serial.list_ebb_ports()
        self.assertIsNone(result)

    @patch('plotink.ebb3_serial.comports')
    def test_comports_type_error(self, mock_comports):
        mock_comports.side_effect = TypeError
        result = ebb3_serial.list_ebb_ports()
        self.assertIsNone(result)


class FindNamedTestCase(unittest.TestCase):
    """Tests for module-level find_named()."""

    @patch('plotink.ebb3_serial.comports')
    def test_find_by_serial_number(self, mock_comports):
        mock_comports.return_value = [
            ('COM3', 'EiBotBoard (COM3)', 'USB VID:PID=04D8:FD92 SER=ABC123 LOCATION=1'),
        ]
        result = ebb3_serial.find_named('ABC123')
        self.assertEqual(result, 'COM3')

    @patch('plotink.ebb3_serial.comports')
    def test_find_by_nickname(self, mock_comports):
        mock_comports.return_value = [
            ('COM3', 'EiBotBoard MyPlotter', 'USB VID:PID=04D8:FD92'),
        ]
        result = ebb3_serial.find_named('MyPlotter')
        self.assertEqual(result, 'COM3')

    @patch('plotink.ebb3_serial.comports')
    def test_not_found(self, mock_comports):
        mock_comports.return_value = [
            ('COM3', 'EiBotBoard Other', 'USB VID:PID=04D8:FD92 SER=XYZ'),
        ]
        result = ebb3_serial.find_named('NonExistent')
        self.assertIsNone(result)

    def test_none_name(self):
        result = ebb3_serial.find_named(None)
        self.assertIsNone(result)


class RecordErrorTestCase(unittest.TestCase):
    """Tests for EBB3.record_error() — only first error is kept."""

    def test_first_error_recorded(self):
        ebb = ebb3_serial.EBB3()
        ebb.record_error("first")
        self.assertEqual(ebb.err, "first")

    def test_second_error_ignored(self):
        ebb = ebb3_serial.EBB3()
        ebb.record_error("first")
        ebb.record_error("second")
        self.assertEqual(ebb.err, "first")
