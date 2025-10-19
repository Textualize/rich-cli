import re
from pathlib import Path
from click.testing import CliRunner
import xml.etree.ElementTree as ET
import pytest

from rich_cli.__main__ import main

ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')


def contains_ansi(s: str) -> bool:
    return bool(ANSI_ESCAPE_RE.search(s))


def validate_svg_structure(svg_content: str) -> bool:
    """Validate SVG structure using XML parsing."""
    try:
        ET.fromstring(svg_content)
        
        if '<svg' not in svg_content:
            return False
            
        has_svg_tag = re.search(r'<svg[^>]*>', svg_content) is not None
        has_closing_svg_tag = '</svg>' in svg_content
        
        return has_svg_tag and has_closing_svg_tag
    except ET.ParseError:
        return False


def validate_html_structure(html_content: str) -> bool:
    """Validate HTML structure using robust parsing that handles real-world HTML output."""
    try:
        lowered = html_content.lower()
        
        has_doctype = '<!doctype html>' in lowered
        has_html_tag = '<html' in lowered
        has_head_tag = '<head' in lowered  
        has_body_tag = '<body' in lowered
        
        if has_doctype:
            if not (has_html_tag and has_head_tag and has_body_tag):
                return False
                
            try:
                clean_html = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
                ET.fromstring(clean_html)
                return True
            except ET.ParseError:
                return validate_html_tag_balance(html_content)
        else:
            return validate_html_tag_balance(html_content)
            
    except Exception:
        return basic_html_sanity_check(html_content)


def basic_html_sanity_check(html_content: str) -> bool:
    """Basic sanity check for HTML content without strict parsing."""
    patterns = [
        r'<[a-zA-Z][^>]*>',  
        r'</[a-zA-Z]+>',    
    ]
    
    has_tags = any(re.search(pattern, html_content) for pattern in patterns)
    
    open_tags = len(re.findall(r'<([a-zA-Z]+)(?:\s[^>]*)?>', html_content))
    close_tags = len(re.findall(r'</([a-zA-Z]+)>', html_content))
    
    reasonable_balance = abs(open_tags - close_tags) < 5
    
    return has_tags and reasonable_balance


def validate_html_tag_balance(html_content: str) -> bool:
    """Validate that HTML tags are properly balanced."""
    try:
        open_tags = []
        tag_pattern = re.compile(r'</?([a-zA-Z][a-zA-Z0-9]*)[^>]*>')
        
        for match in tag_pattern.finditer(html_content):
            tag = match.group(1).lower()
            full_tag = match.group(0)
            
            if full_tag.startswith('</'):  
                if not open_tags or open_tags[-1] != tag:
                    return False 
                open_tags.pop()
            elif not full_tag.endswith('/>'):  
                if tag not in ('br', 'hr', 'img', 'input', 'meta', 'link', '!doctype'):
                    open_tags.append(tag)
        
        return len(open_tags) == 0  
    except Exception:
        return False


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_svg_file(tmp_path):
    return str(tmp_path / "test.svg")


@pytest.fixture
def temp_html_file(tmp_path):
    return str(tmp_path / "test.html")


def assert_styled_and_no_ansi(content: str, *, is_svg: bool = False):
    """Assert that content contains styling and no raw ANSI."""
    assert not contains_ansi(content), "Found raw ANSI escape sequences in output"
    if is_svg:
        assert ('style=' in content or '<style' in content or 'fill=' in content), (
            "No styling detected in SVG output"
        )
    else:
        assert ('style=' in content or '<style' in content or 'class=' in content or 'color:' in content), (
            "No styling detected in HTML output"
        )


# === TESTS START HERE ===


def test_export_svg_with_ansi_preprocessing(runner, temp_svg_file):
    result = runner.invoke(
        main,
        ["-p", "[green]hello[/green]", "--export-svg", temp_svg_file, "--preprocess-ansi"],
    )
    assert result.exit_code == 0, f"Command failed: {result.output}"

    svg = Path(temp_svg_file).read_text()
    assert "hello" in svg and "[green]" not in svg
    assert validate_svg_structure(svg)
    assert_styled_and_no_ansi(svg, is_svg=True)


def test_export_html_with_ansi_preprocessing(runner, temp_html_file):
    result = runner.invoke(
        main,
        ["-p", "[green]hello[/green]", "--export-html", temp_html_file, "--preprocess-ansi"],
    )
    assert result.exit_code == 0
    html = Path(temp_html_file).read_text()
    assert "hello" in html and "[green]" not in html
    assert validate_html_structure(html)
    assert_styled_and_no_ansi(html)


def test_pipe_ansi_to_svg_export(runner, temp_svg_file):
    ansi = "\033[32mhello\033[0m"
    result = runner.invoke(
        main,
        ["--export-svg", temp_svg_file, "-", "--preprocess-ansi"],
        input=ansi,
    )
    assert result.exit_code == 0
    svg = Path(temp_svg_file).read_text()
    assert "hello" in svg
    assert_styled_and_no_ansi(svg, is_svg=True)
    assert validate_svg_structure(svg)


def test_pipe_ansi_to_html_export(runner, temp_html_file):
    ansi = "\033[32mhello\033[0m"
    result = runner.invoke(
        main,
        ["--export-html", temp_html_file, "-", "--preprocess-ansi"],
        input=ansi,
    )
    assert result.exit_code == 0
    html = Path(temp_html_file).read_text()
    assert "hello" in html
    assert_styled_and_no_ansi(html)
    assert validate_html_structure(html)


def test_preprocess_ansi_enabled_svg_styling(runner, temp_svg_file):
    result = runner.invoke(
        main,
        ["--export-svg", temp_svg_file, "-", "--preprocess-ansi"],
        input="\033[32mhello\033[0m",
    )
    assert result.exit_code == 0
    svg = Path(temp_svg_file).read_text()
    assert "hello" in svg
    assert not contains_ansi(svg)
    assert any(tag in svg for tag in ("style=", "fill=", "class="))


def test_preprocess_ansi_enabled_html_styling(runner, temp_html_file):
    ansi = "\033[32mhello\033[0m"
    result = runner.invoke(
        main,
        ["--export-html", temp_html_file, "-", "--preprocess-ansi"],
        input=ansi,
    )
    assert result.exit_code == 0
    html = Path(temp_html_file).read_text()
    assert "hello" in html
    assert not contains_ansi(html)
    assert any(t in html for t in ("style=", "color:", "<style"))


def test_mixed_ansi_and_rich_markup(runner, temp_html_file):
    mixed = "\033[32mANSI green\033[0m and [blue]rich blue[/blue]"
    result = runner.invoke(
        main,
        ["--export-html", temp_html_file, "-", "--preprocess-ansi"],
        input=mixed,
    )
    assert result.exit_code == 0
    html = Path(temp_html_file).read_text()
    assert all(k in html for k in ("ANSI green", "rich blue"))
    assert_styled_and_no_ansi(html)
    assert validate_html_structure(html)


def test_special_characters_handling(runner, temp_html_file):
    special = 'Text <>&"\' and \033[32mANSI\033[0m'
    result = runner.invoke(
        main,
        ["--export-html", temp_html_file, "-", "--preprocess-ansi"],
        input=special,
    )
    assert result.exit_code == 0
    html = Path(temp_html_file).read_text()
    assert "&lt;" in html
    assert "&gt;" in html
    assert "&amp;" in html
    assert "&quot;" in html or "&#34;" in html


def test_unicode_and_binary_safety(runner, temp_html_file):
    uni = "Unicode 中文 Español 🚀\033[32mGreen\033[0m"
    result = runner.invoke(
        main,
        ["--export-html", temp_html_file, "-", "--preprocess-ansi"],
        input=uni,
    )
    assert result.exit_code == 0
    html = Path(temp_html_file).read_text()
    assert "Unicode" in html
    assert "Green" in html
    assert validate_html_structure(html)

