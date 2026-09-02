import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_FILE = COURSE_ROOT / "index.html"
EXAM_FILE = COURSE_ROOT / "exam.html"
LIGHTHOUSE_CONFIG = COURSE_ROOT / "lighthouserc.json"
CI_FILE = COURSE_ROOT / ".github" / "workflows" / "ci.yml"


class LighthouseWebMetricsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta_tags = []
        self.img_tags = []
        self.script_tags = []
        self.has_title = False
        self.title_text = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta":
            self.meta_tags.append(attr_dict)
        elif tag == "img":
            self.img_tags.append(attr_dict)
        elif tag == "script":
            self.script_tags.append(attr_dict)
        elif tag == "title":
            self._in_title = True
            self.has_title = True

    def handle_data(self, data):
        if self._in_title:
            self.title_text += data

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False


class TestLighthouseAndWebVitals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_docs = {
            "index.html": INDEX_FILE.read_text(encoding="utf-8"),
            "exam.html": EXAM_FILE.read_text(encoding="utf-8"),
        }
        for f in sorted(LECTURES_DIR.glob("*.html")):
            cls.all_docs[f.name] = f.read_text(encoding="utf-8")

    def test_01_lighthouserc_configuration_exists_and_valid(self):
        self.assertTrue(LIGHTHOUSE_CONFIG.is_file())
        data = json.loads(LIGHTHOUSE_CONFIG.read_text(encoding="utf-8"))
        self.assertIn("ci", data)
        self.assertIn("assertions", data["ci"]["assert"])

    def test_02_ci_workflow_runs_lighthouse_ci(self):
        self.assertTrue(CI_FILE.is_file())
        ci_content = CI_FILE.read_text(encoding="utf-8")
        self.assertIn("Lighthouse CI", ci_content)

    def test_03_viewport_and_seo_meta_tags(self):
        self.assertEqual(len(self.all_docs), 30)
        for name, html in self.all_docs.items():
            p = LighthouseWebMetricsParser()
            p.feed(html)
            has_viewport = any(
                m.get("name") == "viewport" and "width=device-width" in m.get("content", "")
                for m in p.meta_tags
            )
            self.assertTrue(has_viewport, f"{name} missing viewport")
            self.assertTrue(p.has_title, f"{name} missing title")

    def test_04_touch_targets_and_cls_guarantees(self):
        style_css = (COURSE_ROOT / "style.css").read_text(encoding="utf-8")
        self.assertIn("min-height: 44px", style_css)
        self.assertIn("env(safe-area-inset-bottom", style_css)


if __name__ == "__main__":
    unittest.main()
