#!/usr/bin/env bash

systemctl stop power-monitoring.service
systemctl disable power-monitoring.service

[[ -f "/etc/systemd/system/power-monitoring.service" ]] && \
    rm "/etc/systemd/system/power-monitoring.service"

