import unittest
from weblib.css_frameworks import BootstrapFramework


class TestCSSFrameworkSpacing(unittest.TestCase):
    def setUp(self):
        self.css = BootstrapFramework()

    def test_margin_without_side(self):
        self.assertEqual(self.css.margin(2), "m-2")

    def test_margin_with_side(self):
        self.assertEqual(self.css.margin(3, "t"), "mt-3")

    def test_padding_without_side(self):
        self.assertEqual(self.css.padding(4), "p-4")

    def test_padding_with_side(self):
        self.assertEqual(self.css.padding(5, "e"), "pe-5")


if __name__ == "__main__":
    unittest.main()
