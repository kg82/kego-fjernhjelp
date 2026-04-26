#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch RustDesk for KEGO Data support operator tool (full client, not incoming-only)"""
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("[START] Applying KEGO Data Support (support-klient) customizations...")

# 1. APP_NAME + server config
print("[1/5] Setter APP_NAME og server...")
with open('libs/hbb_common/src/config.rs', 'r') as f:
    config = f.read()

config = re.sub(
    r'"RustDesk"\.to_owned\(\)',
    '"KEGO Data Support".to_owned()',
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
print("  [OK] APP_NAME: 'KEGO Data Support'")
print("  [OK] Server: remote.baksystem.no + RS_PUB_KEY satt")

# 2. Norwegian strings
print("[2/5] Oppdaterer norske strenger...")
with open('src/lang/nb.rs', 'r', encoding='utf-8') as f:
    nb_lang = f.read()

nb_lang = nb_lang.replace(
    '("Your Desktop", "Ditt skrivebord")',
    '("Your Desktop", "Start Fjernhjelp?")'
)
nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan få adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Koble til en ekstern PC ved hjelp av ID og passord.")'
)

with open('src/lang/nb.rs', 'w', encoding='utf-8') as f:
    f.write(nb_lang)
print("  [OK] Your Desktop -> 'Start Fjernhjelp?'")
print("  [OK] desk_tip oppdatert")

# 3. English strings
print("[3/5] Oppdaterer engelske strenger...")
with open('src/lang/en.rs', 'r', encoding='utf-8') as f:
    en_lang = f.read()

en_lang = en_lang.replace(
    '("desk_tip", "Your desktop can be accessed with this ID and password.")',
    '("Your Desktop", "Start Remote Support?"),\n        ("desk_tip", "Connect to a remote PC using the ID and password.")'
)

with open('src/lang/en.rs', 'w', encoding='utf-8') as f:
    f.write(en_lang)
print("  [OK] Your Desktop -> 'Start Remote Support?'")
print("  [OK] desk_tip oppdatert")

# 4. Force dark theme as default
print("[4/5] Tving mørkt tema som standard...")
with open('flutter/lib/common.dart', 'r', encoding='utf-8') as f:
    common = f.read()

common = common.replace(
    'static ThemeMode getThemeModePreference() {\n    return themeModeFromString(bind.mainGetLocalOption(key: kCommConfKeyTheme));\n  }',
    'static ThemeMode getThemeModePreference() {\n    final stored = bind.mainGetLocalOption(key: kCommConfKeyTheme);\n    if (stored.isEmpty || stored == \'system\') return ThemeMode.dark;\n    return themeModeFromString(stored);\n  }'
)

with open('flutter/lib/common.dart', 'w', encoding='utf-8') as f:
    f.write(common)
print("  [OK] Mørkt tema satt som standard")

# 5. Add Kunder button in connection_page.dart
print("[5/5] Legger til Kunder-knapp i connection_page.dart...")
with open('flutter/lib/desktop/pages/connection_page.dart', 'r', encoding='utf-8') as f:
    conn_page = f.read()

kego_import = "import 'package:flutter_hbb/kego_customers.dart';"
if kego_import not in conn_page:
    conn_page = conn_page.replace(
        "// main window right pane",
        f"// main window right pane\n{kego_import}"
    )

inject_before = "            Padding(\n              padding: const EdgeInsets.only(top: 13.0),"
inject_row = "            Row(children: [const KegoCustomersButton()]).paddingOnly(bottom: 4),"
if inject_before in conn_page and inject_row not in conn_page:
    conn_page = conn_page.replace(
        inject_before,
        f"{inject_row}\n{inject_before}"
    )

with open('flutter/lib/desktop/pages/connection_page.dart', 'w', encoding='utf-8') as f:
    f.write(conn_page)
print("  [OK] Kunder-knapp lagt til i connection_page.dart")

print("\n[SUCCESS] Support-klient tilpasninger ferdig!")
