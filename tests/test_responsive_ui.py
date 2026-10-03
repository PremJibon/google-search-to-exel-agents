import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

print("Testing Responsive UI & Component Integrity...")

# 1. Test responsive styles file
with open("src/ui/responsive_styles.py", "r", encoding="utf-8") as f:
    css_content = f.read()

assert "@media screen and (max-width: 768px)" in css_content, "Mobile 768px media query missing"
assert "@media screen and (max-width: 400px)" in css_content, "Small screen 400px media query missing"
assert "@media screen and (min-width: 769px) and (max-width: 1024px)" in css_content, "Tablet media query missing"
assert "@media screen and (min-width: 1025px)" in css_content, "Desktop media query missing"
assert "min-height: 42px" in css_content, "Touch target ergonomics missing"
assert ".responsive-metrics-grid" in css_content, "Responsive metrics grid class missing"
assert "Material Symbols Rounded" in css_content, "Material Symbols icon ligature protection missing"
print("-> PASSED: Responsive CSS media queries, icon protection & touch rules verified!")

# 2. Test components.py
with open("src/ui/components.py", "r", encoding="utf-8") as f:
    comp_content = f.read()

assert "responsive-metrics-grid" in comp_content, "render_metric_cards must use responsive-metrics-grid"
assert "inject_responsive_saas_styles" in comp_content, "inject_responsive_saas_styles must be invoked"
print("-> PASSED: src/ui/components.py properly implements responsive grid!")

# 3. Test voice_component.py
from src.ui.voice_component import render_browser_voice_dictation, render_whisper_voice_recorder, render_voice_input_widget
assert callable(render_browser_voice_dictation), "render_browser_voice_dictation must be callable"
assert callable(render_whisper_voice_recorder), "render_whisper_voice_recorder must be callable"
assert callable(render_voice_input_widget), "render_voice_input_widget must be callable"
print("-> PASSED: src/ui/voice_component.py exports verified!")

# 4. Test Google Map responsive touch features
with open("src/ui/google_map_component.py", "r", encoding="utf-8") as f:
    map_code = f.read()

assert "gestureHandling: 'cooperative'" in map_code, "Google Map must have cooperative touch gestures"
assert "calc(100% - 24px)" in map_code, "Google Map Places input must be responsive"
print("-> PASSED: Google Map mobile gesture handling and responsive input verified!")

print("\n==================================================")
print("ALL RESPONSIVE UI & VOICE COMPONENT CHECKS PASSED 100%!")
print("==================================================")
