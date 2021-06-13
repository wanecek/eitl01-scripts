#!/usr/bin/env bash

[[ -f "./sysstat-monitoring.service" ]] && \
    cp "./sysstat-monitoring.service" "/etc/systemd/system/sysstat-monitoring.service"

systemctl enable sysstat-monitoring.service
systemctl start sysstat-monitoring.service
