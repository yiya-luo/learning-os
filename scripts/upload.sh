#!/bin/bash
#
# WeChat Mini Program automated upload script
#
# ONE-TIME SETUP:
#   1. Go to https://mp.weixin.qq.com → Development → Development Settings
#   2. Generate "upload private key" and save to frontend/private.key
#   3. Add your IP to the whitelist on the same page
#
# Usage:
#   ./scripts/upload.sh "1.0.1" "Bug fixes"     # upload only
#   ./scripts/upload.sh "1.0.1" "Bug fixes" --submit  # upload + submit for review
#

set -euo pipefail

VERSION="${1:-1.0.0}"
DESC="${2:-Update}"
DO_SUBMIT="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$ROOT_DIR/frontend"
KEY_FILE="$FRONTEND_DIR/private.key"
BUILD_DIR="$FRONTEND_DIR/dist/build/mp-weixin"

if [ ! -f "$KEY_FILE" ]; then
  echo "ERROR: private.key not found at $KEY_FILE"
  echo ""
  echo "To get the upload key:"
  echo "  1. Open https://mp.weixin.qq.com → Development → Development Settings"
  echo "  2. Click 'Generate' under 'Upload Key' section"
  echo "  3. Save the downloaded key to: $KEY_FILE"
  exit 1
fi

echo "→ Building mini program..."
cd "$FRONTEND_DIR"
npm run build:mp-weixin

echo "→ Uploading version $VERSION..."
npx miniprogram-ci upload \
  --pp "$BUILD_DIR" \
  --pkp "$KEY_FILE" \
  --appid wx80c67e5edc61479a \
  --uv "$VERSION" \
  --ud "$DESC" \
  --enable-es6 true

echo "→ Upload done."

if [ "$DO_SUBMIT" = "--submit" ]; then
  echo "→ Submitting for review..."
  npx miniprogram-ci submit \
    --pp "$BUILD_DIR" \
    --pkp "$KEY_FILE" \
    --appid wx80c67e5edc61479a \
    --uv "$VERSION" \
    --ud "$DESC"
  echo "→ Review submitted."
fi
