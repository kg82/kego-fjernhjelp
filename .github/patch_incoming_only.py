#!/usr/bin/env python3
import re
with open('libs/hbb_common/src/config.rs', 'r') as f:
    content = f.read()
pattern = r'pub fn is_incoming_only\(\) -> bool \{[^}]*\}'
replacement = 'pub fn is_incoming_only() -> bool {\n    true\n}'
content = re.sub(pattern, replacement, content)
with open('libs/hbb_common/src/config.rs', 'w') as f:
    f.write(content)
print("is_incoming_only() patched to always return true")
