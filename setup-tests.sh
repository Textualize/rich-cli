#!/bin/bash
set -e
cat > test.patch <<'PATCH'
<PASTE the full test.patch content from the problem description here>
PATCH
git apply test.patch
rm test.patch
chmod +x test.sh
