"""Tests for CVSS vector helpers."""

from django.test import SimpleTestCase

from nautobot_device_lifecycle_mgmt.cvss import parse_cvss_vector


class ParseCvssVectorTest(SimpleTestCase):
    """Test the parse_cvss_vector function."""

    def test_v31_vector(self):
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        result = parse_cvss_vector(vector)

        self.assertEqual(result["version"], "3.1")
        self.assertEqual(result["vector"], vector)
        self.assertEqual(result["calculator_url"], f"https://www.first.org/cvss/calculator/3.1#{vector}")
        self.assertEqual(
            [(m["key"], m["value"]) for m in result["metrics"]],
            [("AV", "N"), ("AC", "L"), ("PR", "N"), ("UI", "N"), ("S", "U"), ("C", "H"), ("I", "H"), ("A", "H")],
        )
        self.assertEqual(result["metrics"][0]["name"], "Attack Vector")
        self.assertEqual(result["metrics"][0]["value_name"], "Network")
        self.assertEqual(result["metrics"][4]["name"], "Scope")
        self.assertEqual(result["metrics"][4]["value_name"], "Unchanged")
        self.assertTrue(all(m["description"] for m in result["metrics"]))

    def test_v30_vector(self):
        result = parse_cvss_vector("CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:C/C:L/I:N/A:L")

        self.assertEqual(result["version"], "3.0")
        self.assertEqual(
            [m["value_name"] for m in result["metrics"]],
            ["Local", "High", "High", "Required", "Changed", "Low", "None", "Low"],
        )

    def test_v40_vector(self):
        vector = "CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:A"
        result = parse_cvss_vector(vector)

        self.assertEqual(result["version"], "4.0")
        self.assertEqual(result["calculator_url"], f"https://www.first.org/cvss/calculator/4.0#{vector}")
        metrics = {m["key"]: m for m in result["metrics"]}
        self.assertEqual(metrics["AT"]["name"], "Attack Requirements")
        self.assertEqual(metrics["AT"]["value_name"], "Present")
        self.assertEqual(metrics["UI"]["value_name"], "Active")
        self.assertEqual(metrics["VC"]["name"], "Vulnerable System Confidentiality")
        self.assertEqual(metrics["SA"]["name"], "Subsequent System Availability")
        self.assertEqual(metrics["E"]["value_name"], "Attacked")

    def test_v40_vector_with_environmental_and_supplemental_metrics(self):
        vector = (
            "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N/E:A/CR:H/IR:X/AR:X"
            "/MAV:L/MAC:X/MAT:X/MPR:X/MUI:P/MVC:X/MVI:X/MVA:X/MSC:X/MSI:S/MSA:X/S:P/AU:Y/R:U/V:C/RE:M/U:Red"
        )
        result = parse_cvss_vector(vector)

        self.assertEqual(result["vector"], vector)
        self.assertEqual(len(result["metrics"]), 32)
        self.assertTrue(all(m["description"] for m in result["metrics"]))
        metrics = {m["key"]: m for m in result["metrics"]}
        self.assertEqual((metrics["CR"]["name"], metrics["CR"]["value_name"]), ("Confidentiality Requirement", "High"))
        self.assertEqual((metrics["IR"]["name"], metrics["IR"]["value_name"]), ("Integrity Requirement", "Not Defined"))
        self.assertEqual((metrics["MAV"]["name"], metrics["MAV"]["value_name"]), ("Modified Attack Vector", "Local"))
        self.assertEqual(metrics["MUI"]["value_name"], "Passive")
        self.assertEqual(
            (metrics["MSI"]["name"], metrics["MSI"]["value_name"]), ("Modified Subsequent System Integrity", "Safety")
        )
        self.assertEqual((metrics["S"]["name"], metrics["S"]["value_name"]), ("Safety", "Present"))
        self.assertEqual((metrics["AU"]["name"], metrics["AU"]["value_name"]), ("Automatable", "Yes"))
        self.assertEqual((metrics["R"]["name"], metrics["R"]["value_name"]), ("Recovery", "User"))
        self.assertEqual((metrics["V"]["name"], metrics["V"]["value_name"]), ("Value Density", "Concentrated"))
        self.assertEqual(
            (metrics["RE"]["name"], metrics["RE"]["value_name"]), ("Vulnerability Response Effort", "Moderate")
        )
        self.assertEqual((metrics["U"]["name"], metrics["U"]["value_name"]), ("Provider Urgency", "Red"))

    def test_v31_vector_with_temporal_and_environmental_metrics(self):
        vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:F/RL:O/RC:C/CR:M/IR:X/AR:L/MAV:A/MAC:X/MPR:L/MUI:R/MS:C/MC:N/MI:X/MA:L"
        result = parse_cvss_vector(vector)

        self.assertTrue(all(m["description"] for m in result["metrics"]))
        metrics = {m["key"]: m for m in result["metrics"]}
        self.assertEqual((metrics["E"]["name"], metrics["E"]["value_name"]), ("Exploit Code Maturity", "Functional"))
        self.assertEqual((metrics["RL"]["name"], metrics["RL"]["value_name"]), ("Remediation Level", "Official Fix"))
        self.assertEqual((metrics["RC"]["name"], metrics["RC"]["value_name"]), ("Report Confidence", "Confirmed"))
        self.assertEqual(metrics["CR"]["value_name"], "Medium")
        self.assertEqual(metrics["AR"]["value_name"], "Low")
        self.assertEqual((metrics["MAV"]["name"], metrics["MAV"]["value_name"]), ("Modified Attack Vector", "Adjacent"))
        self.assertEqual(metrics["MAC"]["value_name"], "Not Defined")
        self.assertEqual((metrics["MS"]["name"], metrics["MS"]["value_name"]), ("Modified Scope", "Changed"))
        self.assertEqual((metrics["MC"]["name"], metrics["MC"]["value_name"]), ("Modified Confidentiality", "None"))

    def test_v30_uses_v3_temporal_metrics(self):
        result = parse_cvss_vector("CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:U/RL:W/RC:R")

        self.assertEqual(
            [(m["name"], m["value_name"]) for m in result["metrics"][8:]],
            [
                ("Exploit Code Maturity", "Unproven"),
                ("Remediation Level", "Workaround"),
                ("Report Confidence", "Reasonable"),
            ],
        )

    def test_v2_vector_without_prefix(self):
        vector = "AV:N/AC:L/Au:N/C:P/I:P/A:C"
        result = parse_cvss_vector(vector)

        self.assertEqual(result["version"], "2.0")
        self.assertEqual(
            result["calculator_url"],
            "https://nvd.nist.gov/vuln-metrics/cvss/v2-calculator?vector=%28AV%3AN%2FAC%3AL%2FAu%3AN%2FC%3AP%2FI%3AP%2FA%3AC%29",
        )
        self.assertEqual(
            [(m["name"], m["value_name"]) for m in result["metrics"]],
            [
                ("Access Vector", "Network"),
                ("Access Complexity", "Low"),
                ("Authentication", "None"),
                ("Confidentiality Impact", "Partial"),
                ("Integrity Impact", "Partial"),
                ("Availability Impact", "Complete"),
            ],
        )

    def test_v2_vector_with_parentheses(self):
        result = parse_cvss_vector("(AV:N/AC:L/Au:N/C:P/I:P/A:P)")

        self.assertEqual(result["version"], "2.0")
        self.assertEqual(result["vector"], "AV:N/AC:L/Au:N/C:P/I:P/A:P")

    def test_unrecognized_metric_and_value_keep_raw_text(self):
        result = parse_cvss_vector("CVSS:3.1/AV:Z/XX:Y")

        self.assertEqual(
            result["metrics"],
            [
                {
                    "key": "AV",
                    "name": "Attack Vector",
                    "description": result["metrics"][0]["description"],
                    "value": "Z",
                    "value_name": "Z",
                },
                {"key": "XX", "name": "XX", "description": "", "value": "Y", "value_name": "Y"},
            ],
        )

    def test_blank_segments_are_skipped(self):
        result = parse_cvss_vector("CVSS:3.1/AV:N//AC:L/ /PR:N/UI:N/S:U/C:H/I:H/A:H/")

        self.assertEqual(result["vector"], "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
        self.assertEqual(
            result["calculator_url"],
            "https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        )
        self.assertEqual(result["metrics"][0]["name"], "Attack Vector")
        self.assertEqual(result["metrics"][0]["value_name"], "Network")
        self.assertEqual(len(result["metrics"]), 8)
        self.assertNotIn("", [m["key"] for m in result["metrics"]])

    def test_leading_slash_before_prefix(self):
        result = parse_cvss_vector("/CVSS:3.1/AV:N/AC:L")

        self.assertEqual(result["version"], "3.1")
        self.assertEqual(result["vector"], "CVSS:3.1/AV:N/AC:L")

    def test_blank_segments_in_v2_vector(self):
        result = parse_cvss_vector("AV:N//AC:L/Au:N/C:P/I:P/A:P/")

        self.assertEqual(result["version"], "2.0")
        self.assertEqual(result["vector"], "AV:N/AC:L/Au:N/C:P/I:P/A:P")
        self.assertEqual(result["metrics"][0]["value_name"], "Network")

    def test_malformed_segments_are_skipped(self):
        result = parse_cvss_vector("CVSS:3.1/AV:N/garbage/AC:/:L/PR:N:X/AC:L")

        self.assertEqual(result["vector"], "CVSS:3.1/AV:N/AC:L")
        self.assertEqual([(m["key"], m["value_name"]) for m in result["metrics"]], [("AV", "Network"), ("AC", "Low")])

    def test_empty_or_unsupported_vector(self):
        for vector in (None, "", "   ", "()", "/", "CVSS:3.1/", "CVSS:3.1//", "garbage", "CVSS:9.9/AV:N"):
            with self.subTest(vector=vector):
                self.assertIsNone(parse_cvss_vector(vector))
