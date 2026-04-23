#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch RustDesk for KEGO Data QuickSupport customization"""
import os
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

build_nr = os.environ.get("BUILD_NR", "0")
app_name = f"KEGO Data Fjernhjelp (build-{build_nr})"
print(f"[0/5] Build nr: {build_nr} — app name: '{app_name}'")

# 0. Embed build number into APP_NAME default in config.rs
print("[0/5] Setter build-nummer i APP_NAME...")
with open('libs/hbb_common/src/config.rs', 'r') as f:
    config = f.read()

config = re.sub(
    r'"KEGO Data Fjernhjelp"\.to_owned\(\)',
    f'"{app_name}".to_owned()',
    config
)

# 1a. Patch is_disable_installation() to return true in incoming-only mode.
#     This prevents the "install_tip" / UAC warning card from showing in the Flutter UI.
#     The Flutter code at desktop_home_page.dart checks:
#       if (isWindows && !bind.isDisableInstallation()) { ... show install_tip ... }
#     By returning true when is_incoming_only(), the entire block is skipped.
config = re.sub(
    r'pub fn is_disable_installation\(\) -> bool \{[^}]*\}',
    'pub fn is_disable_installation() -> bool {\n    if is_incoming_only() { return true; }\n    is_some_hard_opton("disable-installation")\n}',
    config
)

with open('libs/hbb_common/src/config.rs', 'w') as f:
    f.write(config)
print(f"  [OK] APP_NAME satt til '{app_name}'")
print("  [OK] is_disable_installation() returnerer true i incoming-only modus")

# 1b. Disable UAC background thread in video_service.rs (defence in depth)
print("[1/5] Disabling UAC background thread...")
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

# 2. Update Norwegian strings
print("[2/5] Updating Norwegian UI strings...")
with open('src/lang/nb.rs', 'r') as f:
    nb_lang = f.read()

nb_lang = nb_lang.replace(
    '("Your Desktop", "Ditt skrivebord")',
    '("Your Desktop", "Start Fjernhjelp?")'
)

nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan fa adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Oppgi ID og engangskoden til representantet fra KEGO Data. Merk: Du kan ikke koble til igjen med samme ID og passord senere.")'
)
nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan f\u00e5 adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Oppgi ID og engangskoden til representantet fra KEGO Data. Merk: Du kan ikke koble til igjen med samme ID og passord senere.")'
)

# Also hide install_tip text entirely for Norwegian
nb_lang = nb_lang.replace(
    '("install_tip", "P\u00e5 grunn av UAC kan RustDesk ikke fungere korrekt i enkelte tillfeller p\u00e5 fjernskrivebordet. For \u00e5 unng\u00e5 UAC klikker du p\u00e5 knappen nedenfor for \u00e5 installere RustDesk p\u00e5 systemet")',
    '("install_tip", "")'
)

with open('src/lang/nb.rs', 'w') as f:
    f.write(nb_lang)
print("  [OK] Norwegian strings updated:")
print("    - 'Your Desktop' -> 'Start Fjernhjelp?'")
print("    - desk_tip -> KEGO Data instruction + note")
print("    - install_tip -> empty (UAC warning hidden)")

# 3. Update English strings
print("[3/5] Updating English UI strings...")
with open('src/lang/en.rs', 'r') as f:
    en_lang = f.read()

en_lang = en_lang.replace(
    '("desk_tip", "Your desktop can be accessed with this ID and password.")',
    '("desk_tip", "Provide your ID and one-time password to the KEGO Data representative. Note: You cannot reconnect with the same ID and password later.")'
)

# Also hide install_tip for English fallback
en_lang = en_lang.replace(
    '("install_tip", "Due to UAC, RustDesk can not work properly as the remote side in some cases. To avoid UAC, please click the button below to install RustDesk to the system.")',
    '("install_tip", "")'
)

with open('src/lang/en.rs', 'w') as f:
    f.write(en_lang)
print("  [OK] English strings updated (desk_tip + install_tip cleared)")

print("\n[SUCCESS] All customizations applied!")
