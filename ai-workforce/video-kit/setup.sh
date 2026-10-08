#!/usr/bin/env bash
# One-time setup for the video kit. Everything comes from PyPI and npm (no Hugging Face / GitHub downloads).
set -euo pipefail
export PIP_CERT="${PIP_CERT:-/root/.ccr/ca-bundle.crt}"
pip install -q imageio-ffmpeg numpy soundfile sherpa-onnx Pillow 2>&1 | grep -v -i warning || true
DEST="${KOKORO_DIR:-$HOME/.cache/edgex-kokoro/kokoro-int8-en-v0_19}"
if [ ! -f "$DEST/model.int8.onnx" ]; then
  # Kokoro-82M (Apache-2.0), int8, packaged for sherpa-onnx inside this npm tarball.
  tmp=$(mktemp -d); (cd "$tmp" && npm pack -q n8n-nodes-ttsbro@0.1.6 >/dev/null && tar xzf n8n-nodes-ttsbro-0.1.6.tgz package/kokoro-int8-en-v0_19)
  mkdir -p "$(dirname "$DEST")"; rm -rf "$DEST"; mv "$tmp/package/kokoro-int8-en-v0_19" "$DEST"; rm -rf "$tmp"
fi
test -f "$DEST/model.int8.onnx" && test -f "$DEST/voices.bin"
NODE_PATH="${NODE_PATH:-/opt/node22/lib/node_modules}" node -e "require('playwright')" 
echo "video kit ready (voice model: $DEST)"
