#!/usr/bin/env bash
#
# Safe full restart for the single-compose stack.
#
# Use this INSTEAD of `docker compose down && up` whenever you need to fully
# restart. Tearing down the rclone container can leave a stale FUSE endpoint on
# the host mount path, which makes the next Hermes start fail with:
#
#   invalid mount config for type "bind": stat .../shared/gdrive_hiorbit:
#   transport endpoint is not connected
#
# This tears down, clears a stale endpoint if present (via a throwaway
# privileged container, so no host sudo), then brings everything back up.
#
# For a config change that only touches Hermes, you don't need this — just:
#   docker compose up -d gateway dashboard
set -euo pipefail

COMPOSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$COMPOSE_DIR"

# Resolve the mount path from .env (default ./shared/gdrive_hiorbit).
GDRIVE_MOUNT_DIR="$(grep -E '^GDRIVE_MOUNT_DIR=' .env 2>/dev/null | cut -d= -f2- || true)"
GDRIVE_MOUNT_DIR="${GDRIVE_MOUNT_DIR:-./shared/gdrive_hiorbit}"
MOUNT_PATH="$(cd "$COMPOSE_DIR" && realpath -m "$GDRIVE_MOUNT_DIR")"
MOUNT_PARENT="$(dirname "$MOUNT_PATH")"
MOUNT_NAME="$(basename "$MOUNT_PATH")"

echo ">> Stopping stack..."
docker compose down

# A live mount or a normal dir stats fine; a stale (disconnected) FUSE endpoint
# returns ENOTCONN. Only then force-clear it.
if ! stat "$MOUNT_PATH" >/dev/null 2>&1; then
  echo ">> Stale FUSE endpoint at $MOUNT_PATH — clearing..."
  docker run --rm --privileged --pid=host \
    -v "$MOUNT_PARENT:/x:rshared" \
    alpine sh -c "umount -l /x/$MOUNT_NAME 2>/dev/null || true"
  if stat "$MOUNT_PATH" >/dev/null 2>&1; then
    echo ">> Endpoint cleared."
  else
    echo "!! Could not clear $MOUNT_PATH automatically." >&2
    echo "!! Run: sudo umount -l $MOUNT_PATH" >&2
    exit 1
  fi
fi

echo ">> Starting stack (rclone first, Hermes waits for healthy mount)..."
docker compose up -d --build

echo ">> Status:"
docker compose ps
