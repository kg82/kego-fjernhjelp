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
print(f"[0/4] Build nr: {build_nr} — app name: '{app_name}'")

# 0. Embed build number into APP_NAME default in config.rs
print("[0/4] Setter build-nummer i APP_NAME...")
with open('libs/hbb_common/src/config.rs', 'r') as f:
    config = f.read()

config = re.sub(
    r'"KEGO Data Fjernhjelp"\.to_owned\(\)',
    f'"{app_name}".to_owned()',
    config
)

with open('libs/hbb_common/src/config.rs', 'w') as f:
    f.write(config)
print(f"  [OK] APP_NAME satt til '{app_name}'")

# 1. Disable UAC warning in incoming-only mode
print("[1/4] Disabling UAC warning...")
with open('src/server/video_service.rs', 'r') as f:
    video_svc = f.read()

video_svc = re.sub(
    r'if !crate::platform::is_installed\(\) && !crate::platform::is_root\(\) \{',
    'if !config::is_incoming_only() && !crate::platform::is_installed() && !crate::platform::is_root() {',
    video_svc
)

with open('src/server/video_service.rs', 'w') as f:
    f.write(video_svc)
print("  [OK] UAC elevation check skipped in incoming-only mode")

# 2. Update Norwegian strings
print("[2/4] Updating Norwegian UI strings...")
with open('src/lang/nb.rs', 'r') as f:
    nb_lang = f.read()

# Replace "Ditt skrivebord" -> "Start Fjernhjelp?"
nb_lang = nb_lang.replace(
    '("Your Desktop", "Ditt skrivebord")',
    '("Your Desktop", "Start Fjernhjelp?")'
)

# Replace desk_tip
nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan fa adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Oppgi ID og engangskoden til representantet fra KEGO Data. Merk: Du kan ikke koble til igjen med samme ID og passord senere.")'
)
# Also try the original Norwegian form (with special chars)
nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan f\u00e5 adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Oppgi ID og engangskoden til representantet fra KEGO Data. Merk: Du kan ikke koble til igjen med samme ID og passord senere.")'
)

with open('src/lang/nb.rs', 'w') as f:
    f.write(nb_lang)
print("  [OK] Norwegian strings updated:")
print("    - 'Your Desktop' -> 'Start Fjernhjelp?'")
print("    - desk_tip -> KEGO Data instruction + note")

# 3. Update English strings (fallback for mixed language systems)
print("[3/4] Updating English UI strings...")
with open('src/lang/en.rs', 'r') as f:
    en_lang = f.read()

en_lang = en_lang.replace(
    '("desk_tip", "Your desktop can be accessed with this ID and password.")',
    '("desk_tip", "Provide your ID and one-time password to the KEGO Data representative. Note: You cannot reconnect with the same ID and password later.")'
)

with open('src/lang/en.rs', 'w') as f:
    f.write(en_lang)
print("  [OK] English desk_tip updated with reconnection note")

print("\n[SUCCESS] All customizations applied!")
