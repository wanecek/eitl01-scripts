#!/usr/bin/env bash

[[ -f "./power-monitoring.service" ]] && \
    cp "./power-monitoring.service" "/etc/systemd/system/power-monitoring.service"

systemctl enable power-monitoring.service
systemctl start power-monitoring.service
