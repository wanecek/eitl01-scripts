#!/bin/bash

set -eou

confirm() {
  while true; do
    read -r -p "$* [y/n]: " yn < /dev/tty
    case $yn in
      [Yy]*) return 0  ;;
      [Nn]*) return 1  ;;
    esac
  done
}

main() {
  [[ -f "cfg/vnstat.conf" ]] && \
    confirm "Do you wish to overwrite vnstat.conf?" && \
    scp "cfg/vnstat.conf" "stellar:/root/vnstat.conf"

  [[ -f "cfg/stellar-core.cfg" ]] && \
    confirm "Do you wish to overwrite stellar-conf?" && \
    scp "cfg/stellar-core.cfg" "stellar:/etc/stellar/stellar-core.cfg"
}

main
