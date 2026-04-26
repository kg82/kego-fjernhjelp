#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch RustDesk for KEGO Data QuickSupport customization"""
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("[START] Applying KEGO Data Fjernhjelp (kundeklient) customizations...")

# 1. Patch is_disable_installation() + keep config.rs open for server config below
print("[1/7] Patcher is_disable_installation() i config.rs...")
with open('libs/hbb_common/src/config.rs', 'r') as f:
    config = f.read()

config = re.sub(
    r'pub fn is_disable_installation\(\) -> bool \{[^}]*\}',
    'pub fn is_disable_installation() -> bool {\n    if is_incoming_only() { return true; }\n    is_some_hard_opton("disable-installation")\n}',
    config
)

with open('libs/hbb_common/src/config.rs', 'w') as f:
    f.write(config)
print("  [OK] is_disable_installation() returnerer true i incoming-only modus")

# 2. Disable UAC background thread in video_service.rs
print("[2/7] Disabling UAC background thread...")
with open('src/server/video_service.rs', 'r') as f:
    video_svc = f.read()

video_svc = re.sub(
    r'if !crate::platform::is_installed\(\) && !crate::platform::is_root\(\) \{',
    'if !config::is_incoming_only() && !crate::platform::is_installed() && !crate::platform::is_root() {',
    video_svc
)

with open('src/server/video_service.rs', 'w') as f:
    f.write(video_svc)
print("  [OK] UAC elevation thread skipped in incoming-only mode")

# 3. Norwegian strings
print("[3/7] Oppdaterer norske strenger...")
with open('src/lang/nb.rs', 'r', encoding='utf-8') as f:
    nb_lang = f.read()

nb_lang = nb_lang.replace(
    '("Your Desktop", "Ditt skrivebord")',
    '("Your Desktop", "Start Fjernhjelp?")'
)
nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan få adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Del ID og passord med representanter fra KEGO Data.")'
)
nb_lang = nb_lang.replace(
    '("install_tip", "På grunn av UAC kan RustDesk ikke fungere korrekt i enkelte tillfeller på fjernskrivebordet. For å unngå UAC klikker du på knappen nedenfor for å installere RustDesk på systemet")',
    '("install_tip", "")'
)

with open('src/lang/nb.rs', 'w', encoding='utf-8') as f:
    f.write(nb_lang)
print("  [OK] Your Desktop -> 'Start Fjernhjelp?'")
print("  [OK] desk_tip og install_tip oppdatert")

# 4. English strings
print("[4/7] Oppdaterer engelske strenger...")
with open('src/lang/en.rs', 'r', encoding='utf-8') as f:
    en_lang = f.read()

en_lang = en_lang.replace(
    '("desk_tip", "Your desktop can be accessed with this ID and password.")',
    '("Your Desktop", "Start Remote Support?"),\n        ("desk_tip", "Share your ID and password with KEGO Data representatives.")'
)
en_lang = en_lang.replace(
    '("install_tip", "Due to UAC, RustDesk can not work properly as the remote side in some cases. To avoid UAC, please click the button below to install RustDesk to the system.")',
    '("install_tip", "")'
)

with open('src/lang/en.rs', 'w', encoding='utf-8') as f:
    f.write(en_lang)
print("  [OK] Your Desktop -> 'Start Remote Support?'")
print("  [OK] desk_tip og install_tip oppdatert")

# 5. Hide 'powered by RustDesk' in incoming-only mode (common.dart)
print("[5/7] Hiding 'powered by RustDesk'...")
with open('flutter/lib/common.dart', 'r', encoding='utf-8') as f:
    common = f.read()

common = re.sub(
    r'Widget loadPowered\(BuildContext context\) \{[^}]*if \(bind\.mainGetBuildinOption\(key: "hide-powered-by-me"\) == \'Y\'\) \{[^}]*\}',
    'Widget loadPowered(BuildContext context) {\n  if (bind.isIncomingOnly() || bind.mainGetBuildinOption(key: "hide-powered-by-me") == \'Y\') {\n    return SizedBox.shrink();\n  }',
    common,
    flags=re.DOTALL
)

with open('flutter/lib/common.dart', 'w', encoding='utf-8') as f:
    f.write(common)
print("  [OK] 'powered by RustDesk' skjult i incoming-only modus")

# 6. Configure custom RustDesk server and public key
print("[6/7] Konfigurerer server og RS_PUB_KEY...")
with open('libs/hbb_common/src/config.rs', 'r') as f:
    config_rs = f.read()

config_rs = re.sub(
    r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\["rs-ny\.rustdesk\.com"\];',
    'pub const RENDEZVOUS_SERVERS: &[&str] = &["remote.baksystem.no"];',
    config_rs
)
config_rs = re.sub(
    r'pub const RS_PUB_KEY: &str = "[^"]+";',
    'pub const RS_PUB_KEY: &str = "1bpTsEiTj4LHyQkGFImLJ0hYA1cmMzogalPczbsKOlU=";',
    config_rs
)

with open('libs/hbb_common/src/config.rs', 'w') as f:
    f.write(config_rs)
print("  [OK] Server: remote.baksystem.no + RS_PUB_KEY satt")

# 7. Force dark theme as default
print("[7/7] Tving mørkt tema som standard...")
with open('flutter/lib/common.dart', 'r', encoding='utf-8') as f:
    common = f.read()

common = common.replace(
    'static ThemeMode getThemeModePreference() {\n    return themeModeFromString(bind.mainGetLocalOption(key: kCommConfKeyTheme));\n  }',
    'static ThemeMode getThemeModePreference() {\n    final stored = bind.mainGetLocalOption(key: kCommConfKeyTheme);\n    if (stored.isEmpty || stored == \'system\') return ThemeMode.dark;\n    return themeModeFromString(stored);\n  }'
)

with open('flutter/lib/common.dart', 'w', encoding='utf-8') as f:
    f.write(common)
print("  [OK] Mørkt tema satt som standard")

# 8. Strip all languages except nb and en from lang.rs
print("[8/8] Fjerner alle språk unntatt norsk og engelsk fra lang.rs...")
with open('src/lang.rs', 'r') as f:
    lang_rs = f.read()

lang_rs = re.sub(
    r'mod ar;.*?mod fi;\n',
    'mod en;\nmod nb;\n',
    lang_rs,
    flags=re.DOTALL
)
lang_rs = re.sub(
    r'pub const LANGS: &\[.*?\];',
    'pub const LANGS: &[(&str, &str)] = &[\n    ("en", "English"),\n    ("nb", "Norsk bokmål"),\n];',
    lang_rs,
    flags=re.DOTALL
)
lang_rs = re.sub(
    r'    let m = match lang\.as_str\(\) \{.*?_ => en::T\.deref\(\),\n    \};',
    '    let m = match lang.as_str() {\n        "nb" => nb::T.deref(),\n        _ => en::T.deref(),\n    };',
    lang_rs,
    flags=re.DOTALL
)

with open('src/lang.rs', 'w') as f:
    f.write(lang_rs)
print("  [OK] Kun norsk (nb) og engelsk (en) kompilert")

print("\n[SUCCESS] Kundeklient-tilpasninger ferdig!")
