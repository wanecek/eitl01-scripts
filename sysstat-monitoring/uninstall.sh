#!/usr/bin/env bash

systemctl stop sysstat-monitoring.service
systemctl disable sysstat-monitoring.service

[[ -f "/etc/systemd/system/sysstat-monitoring.service" ]] && \
    rm "/etc/systemd/system/sysstat-monitoring.service"

