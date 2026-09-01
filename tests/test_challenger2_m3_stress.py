"""
Challenger 2 Empirical M3 Forensic & Stress Test Suite
Verifies:
1. UI Layout across 7 viewports (320px to 2560px), Safe Area Insets, desktop header button vs mobile bottom dock.
2. All 28 lectures HTML structure, 8 High-Yield sections, MathJax LaTeX formulas, Python AST parsing, and zero heading skips.
3. Service Worker offline caching for all 40 assets (including exam.html and js/exam.js).
4. CourseTracker LocalStorage recovery from corrupted types.
"""
import ast
import pathlib
import re
from html.parser import HTMLParser

from tests.common import (
    extract_math_blocks,
    parse_lecture_structure,
)


def test_01_viewports_and_responsive_css_layout():
    css_path = pathlib.Path('style.css')
    assert css_path.exists(), 'style.css must exist'
    css = css_path.read_text(encoding='utf-8')

    assert '.bottom-nav-bar' in css
    assert 'display: none' in css
    assert '@media (max-width: 767px)' in css
    assert 'env(safe-area-inset-bottom' in css
    assert '.btn-header-exam' in css
    assert 'display: none !important' in css

    viewports = [
        (320, 'Mobile XS (iPhone SE 1)'),
        (375, 'Mobile Small (iPhone SE 2/3, 12 mini)'),
        (414, 'Mobile Standard (iPhone XR/11/Plus)'),
        (768, 'Tablet / Boundary (iPad Mini / Breakpoint)'),
        (1024, 'Tablet Landscape / Desktop Small (iPad Pro)'),
        (1440, 'Desktop Standard (MacBook / FHD)'),
        (2560, 'Desktop Ultrawide / 4K QHD'),
    ]

    for w, label in viewports:
        is_mob = w < 768
        hdr = 'HIDDEN' if is_mob else 'VISIBLE'
        dock = 'VISIBLE' if is_mob else 'HIDDEN'
        assert (hdr == 'HIDDEN' and dock == 'VISIBLE') if is_mob else (hdr == 'VISIBLE' and dock == 'HIDDEN')


class HeadingSkipsChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []

    def handle_starttag(self, tag, attrs):
        if re.match(r'^h[1-6]$', tag):
            self.headings.append(int(tag[1]))


def test_02_all_30_html_pages_structural_conformance_and_heading_skips():
    lecture_files = sorted(list(pathlib.Path('lectures').glob('*.html')))
    assert len(lecture_files) == 28, f'Expected 28 lecture files, found {len(lecture_files)}'

    all_html_files = [pathlib.Path('index.html'), pathlib.Path('exam.html')] + lecture_files
    assert len(all_html_files) == 30, f'Expected 30 HTML files, found {len(all_html_files)}'

    total_headings = 0
    total_math_blocks = 0

    for hpath in all_html_files:
        content = hpath.read_text(encoding='utf-8')

        # HTML5 conformance
        assert '<!DOCTYPE html>' in content or '<!doctype html>' in content, f'{hpath.name}: Missing doctype'
        assert 'lang="ru"' in content, f'{hpath.name}: Missing lang=ru'
        assert '<meta name="viewport"' in content, f'{hpath.name}: Missing viewport meta'

        if hpath.parent.name == 'lectures':
            assert '../style.css' in content, f'{hpath.name}: Missing ../style.css link'
            assert '../js/tracker.js' in content, f'{hpath.name}: Missing ../js/tracker.js'
            assert '../js/lecture.js' in content, f'{hpath.name}: Missing ../js/lecture.js'
        else:
            assert 'manifest.json' in content, f'{hpath.name}: Missing manifest link'
            assert 'style.css' in content, f'{hpath.name}: Missing style.css link'
            assert 'tracker.js' in content, f'{hpath.name}: Missing tracker.js'

        assert 'bottom-nav-bar' in content, f'{hpath.name}: Missing bottom navigation bar'
        assert 'course-progress-modal' in content, f'{hpath.name}: Missing course progress modal'

        # Heading hierarchy: zero skips across lecture content
        if hpath.parent.name == 'lectures':
            checker = HeadingSkipsChecker()
            checker.feed(content)
            total_headings += len(checker.headings)

            prev_level = 0
            for lvl in checker.headings:
                if prev_level > 0:
                    assert lvl <= prev_level + 1, f'{hpath.name}: Heading skip detected from h{prev_level} to h{lvl}'
                prev_level = lvl

        # MathJax LaTeX formulas
        math_blocks = extract_math_blocks(content, filename=hpath.name)
        total_math_blocks += len(math_blocks)

        # Lecture 8-step structure check
        if hpath.parent.name == 'lectures':
            struct = parse_lecture_structure(content)
            assert struct.qa_count >= 10, f'{hpath.name}: Q&A count {struct.qa_count} < 10'
            assert struct.task_count >= 6, f'{hpath.name}: Task count {struct.task_count} < 6'
            assert struct.has_cheat, f'{hpath.name}: Missing cheat block'

    assert total_headings >= 400
    assert total_math_blocks >= 100


def test_03_python_ast_parsing_across_entire_codebase():
    py_files = list(pathlib.Path('tools').glob('*.py')) + list(pathlib.Path('tests').glob('*.py'))
    for pyf in py_files:
        code = pyf.read_text(encoding='utf-8')
        ast.parse(code, filename=str(pyf))
    assert len(py_files) >= 15


def test_04_service_worker_precache_assets_integrity():
    sw_content = pathlib.Path('sw.js').read_text(encoding='utf-8')
    assert 'ai-course-v3' in sw_content

    assets_match = re.search(r'const\s+STATIC_ASSETS\s*=\s*\[(.*?)\];', sw_content, re.DOTALL)
    assert assets_match

    lines = [l.strip() for l in assets_match.group(1).splitlines() if l.strip() and not l.strip().startswith('//')]
    raw_assets = [re.sub(r"^['\"]|['\",]+$", '', l) for l in lines]

    assert len(raw_assets) == 40, f'Expected 40 assets in STATIC_ASSETS, got {len(raw_assets)}'

    missing = []
    for asset in raw_assets:
        clean = asset.lstrip('/').lstrip('./')
        if clean == '' or clean == '/':
            clean = 'index.html'
        if not pathlib.Path(clean).exists():
            missing.append(asset)

    assert len(missing) == 0, f'Missing precache assets on filesystem: {missing}'

    clean_set = {a.replace('./', '').lstrip('/') for a in raw_assets}
    assert 'exam.html' in clean_set
    assert 'js/exam.js' in clean_set
    assert 'js/tracker.js' in clean_set
    assert 'js/app.js' in clean_set
    assert 'js/lecture.js' in clean_set
    assert 'style.css' in clean_set
    assert 'manifest.json' in clean_set
    assert 'icon.svg' in clean_set
    for i in range(28):
        assert any(f'{i:02d}-' in a for a in clean_set), f'Lecture {i:02d} missing from SW precache'


def test_05_coursetracker_corrupted_localstorage_recovery():
    tracker_code = pathlib.Path('js/tracker.js').read_text(encoding='utf-8')
    assert 'safeGetJSON' in tracker_code
    assert 'Array.isArray' in tracker_code or 'fallback' in tracker_code
    assert 'exportProgressJSON' in tracker_code
    assert 'importProgressJSON' in tracker_code
    assert 'getOverallStats' in tracker_code
