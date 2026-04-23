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
config = re.sub(
    r'pub fn is_disable_installation\(\) -> bool \{[^}]*\}',
    'pub fn is_disable_installation() -> bool {\n    if is_incoming_only() { return true; }\n    is_some_hard_opton("disable-installation")\n}',
    config
)

with open('libs/hbb_common/src/config.rs', 'w') as f:
    f.write(config)
print(f"  [OK] APP_NAME satt til '{app_name}'")
print("  [OK] is_disable_installation() returnerer true i incoming-only modus")

# 1b. Disable UAC background thread in video_service.rs
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
with open('src/lang/nb.rs', 'r', encoding='utf-8') as f:
    nb_lang = f.read()

# Replace desk_tip with new text (UTF-8 aware)
nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan få adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Del ID og passord med representanter fra KEGO Data.")'
)

# Hide install_tip
nb_lang = nb_lang.replace(
    '("install_tip", "På grunn av UAC kan RustDesk ikke fungere korrekt i enkelte tillfeller på fjernskrivebordet. For å unngå UAC klikker du på knappen nedenfor for å installere RustDesk på systemet")',
    '("install_tip", "")'
)

with open('src/lang/nb.rs', 'w', encoding='utf-8') as f:
    f.write(nb_lang)
print("  [OK] Norwegian strings updated:")
print("    - desk_tip -> 'Del ID og passord med representanter fra KEGO Data.'")
print("    - install_tip -> empty (UAC warning hidden)")

# 3. Update English strings
print("[3/5] Updating English UI strings...")
with open('src/lang/en.rs', 'r', encoding='utf-8') as f:
    en_lang = f.read()

en_lang = en_lang.replace(
    '("desk_tip", "Your desktop can be accessed with this ID and password.")',
    '("desk_tip", "Share your ID and password with KEGO Data representatives.")'
)

en_lang = en_lang.replace(
    '("install_tip", "Due to UAC, RustDesk can not work properly as the remote side in some cases. To avoid UAC, please click the button below to install RustDesk to the system.")',
    '("install_tip", "")'
)

# 4. Hide "powered by RustDesk" in incoming-only mode (common.dart)
print("[4/5] Hiding 'powered by RustDesk'...")
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
print("  [OK] 'powered by RustDesk' hidden in incoming-only mode")

with open('src/lang/en.rs', 'w', encoding='utf-8') as f:
    f.write(en_lang)
print("  [OK] English strings updated (desk_tip + install_tip)")

print("\n[SUCCESS] All customizations applied!")
