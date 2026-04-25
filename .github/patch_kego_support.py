#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch RustDesk for KEGO Data support operator tool (full client, not incoming-only)"""
import os
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

build_nr = os.environ.get("BUILD_NR", "0")
app_name = f"KEGO Data Support (build-{build_nr})"
print(f"[0/4] Build nr: {build_nr} — app name: '{app_name}'")

# 1. APP_NAME + server config
print("[1/4] Setter APP_NAME og server...")
with open('libs/hbb_common/src/config.rs', 'r') as f:
    config = f.read()

config = re.sub(
    r'"RustDesk"\.to_owned\(\)',
    f'"{app_name}".to_owned()',
    config
)

config = re.sub(
    r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\["rs-ny\.rustdesk\.com"\];',
    'pub const RENDEZVOUS_SERVERS: &[&str] = &["remote.baksystem.no"];',
    config
)

config = re.sub(
    r'pub const RS_PUB_KEY: &str = "[^"]+";',
    'pub const RS_PUB_KEY: &str = "1bpTsEiTj4LHyQkGFImLJ0hYA1cmMzogalPczbsKOlU=";',
    config
)

with open('libs/hbb_common/src/config.rs', 'w') as f:
    f.write(config)
print(f"  [OK] APP_NAME: '{app_name}'")
print("  [OK] Server: remote.baksystem.no + RS_PUB_KEY satt")

# 2. Norske strenger
print("[2/4] Oppdaterer norske strenger...")
with open('src/lang/nb.rs', 'r', encoding='utf-8') as f:
    nb_lang = f.read()

nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan få adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Koble til en ekstern PC ved hjelp av ID og passord.")'
)

with open('src/lang/nb.rs', 'w', encoding='utf-8') as f:
    f.write(nb_lang)
print("  [OK] desk_tip oppdatert")

# 3. Engelske strenger
print("[3/4] Oppdaterer engelske strenger...")
with open('src/lang/en.rs', 'r', encoding='utf-8') as f:
    en_lang = f.read()

en_lang = en_lang.replace(
    '("desk_tip", "Your desktop can be accessed with this ID and password.")',
    '("desk_tip", "Connect to a remote PC using the ID and password.")'
)

with open('src/lang/en.rs', 'w', encoding='utf-8') as f:
    f.write(en_lang)
print("  [OK] desk_tip oppdatert")

# 4. Tving mørkt tema
print("[4/4] Tving mørkt tema som standard...")
with open('flutter/lib/common.dart', 'r', encoding='utf-8') as f:
    common = f.read()

common = common.replace(
    'static ThemeMode getThemeModePreference() {\n    return themeModeFromString(bind.mainGetLocalOption(key: kCommConfKeyTheme));\n  }',
    'static ThemeMode getThemeModePreference() {\n    final stored = bind.mainGetLocalOption(key: kCommConfKeyTheme);\n    if (stored.isEmpty || stored == \'system\') return ThemeMode.dark;\n    return themeModeFromString(stored);\n  }'
)

with open('flutter/lib/common.dart', 'w', encoding='utf-8') as f:
    f.write(common)
print("  [OK] Mørkt tema satt som standard")

print("\n[SUCCESS] Support-klient tilpasninger ferdig!")
