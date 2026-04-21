#!/usr/bin/env python3
"""Patch RustDesk for KEGO Data QuickSupport customization"""
import re

# 1. Disable UAC warning in incoming-only mode
print("[1/3] Disabling UAC warning...")
with open('src/server/video_service.rs', 'r') as f:
    video_svc = f.read()

# Find is_installed() and is_root() check, add incoming_only check
video_svc = re.sub(
    r'if !crate::platform::is_installed\(\) && !crate::platform::is_root\(\) \{',
    'if !config::is_incoming_only() && !crate::platform::is_installed() && !crate::platform::is_root() {',
    video_svc
)

with open('src/server/video_service.rs', 'w') as f:
    f.write(video_svc)
print("  ✓ UAC elevation check skipped in incoming-only mode")

# 2. Update Norwegian strings
print("[2/3] Updating Norwegian UI strings...")
with open('src/lang/nb.rs', 'r') as f:
    nb_lang = f.read()

# Replace "Ditt skrivebord" → "Start Fjernhjelp?"
nb_lang = nb_lang.replace(
    '("Your Desktop", "Ditt skrivebord")',
    '("Your Desktop", "Start Fjernhjelp?")'
)

# Replace desk_tip
nb_lang = nb_lang.replace(
    '("desk_tip", "Du kan få adgang til ditt skrivebord med denne ID og passord.")',
    '("desk_tip", "Oppgi ID og engangskoden til representantet fra KEGO Data. Merk: Du kan ikke koble til igjen med samme ID og passord senere.")'
)

with open('src/lang/nb.rs', 'w') as f:
    f.write(nb_lang)
print("  ✓ Norwegian strings updated:")
print("    - 'Your Desktop' → 'Start Fjernhjelp?'")
print("    - desk_tip → KEGO Data instruction + note")

# 3. Update English strings (fallback for mixed language systems)
print("[3/3] Updating English UI strings...")
with open('src/lang/en.rs', 'r') as f:
    en_lang = f.read()

# Add note about single-use password to English desk_tip
en_lang = en_lang.replace(
    '("desk_tip", "Your desktop can be accessed with this ID and password.")',
    '("desk_tip", "Provide your ID and one-time password to the KEGO Data representative. Note: You cannot reconnect with the same ID and password later.")'
)

with open('src/lang/en.rs', 'w') as f:
    f.write(en_lang)
print("  ✓ English desk_tip updated with reconnection note")

print("\n✅ All customizations applied!")
