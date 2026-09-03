#!/usr/bin/env bash
# Collect CI artifacts into RHTLC-friendly release filenames (executables only).
set -euo pipefail

ARTIFACTS_DIR="${1:-artifacts}"
OUT_DIR="${2:-release}"

mkdir -p "$OUT_DIR"

declare -A MAP=(
  ["rhtlc-wstunnel-x86_64-unknown-linux-musl"]="rhtlc-wstunnel-linux-amd64"
  ["rhtlc-wstunnel-aarch64-unknown-linux-musl"]="rhtlc-wstunnel-linux-arm64"
  ["rhtlc-wstunnel-x86_64-apple-darwin"]="rhtlc-wstunnel-macos-amd64"
  ["rhtlc-wstunnel-aarch64-apple-darwin"]="rhtlc-wstunnel-macos-arm64"
  ["rhtlc-wstunnel-x86_64-pc-windows-msvc"]="rhtlc-wstunnel-windows-amd64.exe"
  ["rhtlc-wstunnel-aarch64-pc-windows-msvc"]="rhtlc-wstunnel-windows-arm64.exe"
)

for artifact in "${!MAP[@]}"; do
  src_dir="${ARTIFACTS_DIR}/${artifact}"
  if [[ ! -d "$src_dir" ]]; then
    echo "ERROR: missing artifact directory: $src_dir" >&2
    exit 1
  fi
  src_bin="$(find "$src_dir" -maxdepth 1 -type f ! -name '.*' | head -1)"
  if [[ -z "$src_bin" ]]; then
    echo "ERROR: no binary found under $src_dir" >&2
    exit 1
  fi
  dest="${OUT_DIR}/${MAP[$artifact]}"
  cp "$src_bin" "$dest"
  chmod +x "$dest" 2>/dev/null || true
  echo "Prepared ${dest}"
done

(
  cd "$OUT_DIR"
  sha256sum rhtlc-wstunnel-* > checksums.sha256
)

echo "Release assets in ${OUT_DIR}:"
ls -la "$OUT_DIR"
