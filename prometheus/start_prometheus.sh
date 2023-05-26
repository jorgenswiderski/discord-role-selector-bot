#!/bin/bash

envsubst < alertmanager.template.yml > alertmanager.yml

# Stop Prometheus
prometheus_pid=$(pgrep -f prometheus)
if [[ -n $prometheus_pid ]]; then
  echo "Stopping Prometheus (PID: $prometheus_pid)..."
  kill $prometheus_pid
  sleep 5
fi

# Stop Alertmanager
alertmanager_pid=$(pgrep -f alertmanager)
if [[ -n $alertmanager_pid ]]; then
  echo "Stopping Alertmanager (PID: $alertmanager_pid)..."
  kill $alertmanager_pid
  sleep 5
fi

# Start Prometheus
echo "Starting Prometheus..."
./home/ec2-user/prometheus-2.32.0.linux-amd64/prometheus

# Start Alertmanager
echo "Starting Alertmanager..."
./home/ec2-user/alertmanager-0.25.0.linux-amd64/alertmanager

echo "Prometheus and Alertmanager restarted successfully."
