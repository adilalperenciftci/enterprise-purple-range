import unittest

from avr.network_detection import detect_proftpd_modcopy


class NetworkDetectionTests(unittest.TestCase):
    def test_modcopy_sequence_alerts(self) -> None:
        result = detect_proftpd_modcopy(
            [b"SITE CPFR /proc/self/cmdline\r\n", b"SITE CPTO /var/www/html/proof.php\r\n"],
            complete=True,
        )
        self.assertEqual(result.verdict, "SUSPICIOUS")
        self.assertEqual(result.reason_codes, ("EPR-NET-PROFTPD-MODCOPY",))

    def test_normal_ftp_is_benign(self) -> None:
        result = detect_proftpd_modcopy([b"USER anonymous\r\n", b"LIST\r\n"], complete=True)
        self.assertEqual(result.verdict, "BENIGN")

    def test_missing_stream_is_not_evaluable(self) -> None:
        result = detect_proftpd_modcopy([], complete=False)
        self.assertEqual(result.verdict, "NOT_EVALUABLE")

    def test_oversized_stream_is_not_evaluable(self) -> None:
        result = detect_proftpd_modcopy([b"x" * (1024 * 1024 + 1)], complete=True)
        self.assertEqual(result.verdict, "NOT_EVALUABLE")


if __name__ == "__main__":
    unittest.main()
