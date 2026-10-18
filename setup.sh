#!/usr/bin/env bash
# One-time (per fresh machine) setup: builds the phonemizer and downloads the voice model into .tools/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; T="$ROOT/.tools"; mkdir -p "$T"; cd "$T"
if [ ! -x espeak/bin/espeak-ng ]; then
  [ -d espeak-ng ] || git clone -q --depth 1 https://github.com/espeak-ng/espeak-ng.git
  cmake -S espeak-ng -B espeak-ng/build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$T/espeak" \
    -DUSE_MBROLA=OFF -DUSE_LIBSONIC=OFF -DUSE_LIBPCAUDIO=OFF -DUSE_SPEECHPLAYER=OFF -DUSE_KLATT=OFF -DUSE_ASYNC=OFF >/dev/null
  cmake --build espeak-ng/build -j"$(nproc)" >/dev/null && cmake --install espeak-ng/build >/dev/null
fi
[ -d kokoro-onnx ] || git clone -q --depth 1 https://github.com/thewh1teagle/kokoro-onnx.git
B=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -f voices-v1.0.bin ] || curl -sSL -o voices-v1.0.bin "$B/voices-v1.0.bin"
[ -f kokoro-v1.0.int8.onnx ] || curl -sSL -o kokoro-v1.0.int8.onnx "$B/kokoro-v1.0.int8.onnx"
python3 -c "import onnxruntime, numpy, scipy, PIL" || pip install --break-system-packages -q onnxruntime numpy scipy pillow
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
echo "setup ok"
