#!/bin/bash

# Generate Alertmanager configuration
envsubst < prometheus/alertmanager.template.yml > prometheus/alertmanager.yml
echo "Generated Alertmanager configuration."

# Stop Prometheus
prometheus_pid=$(pgrep -f prometheus)
if [[ -n $prometheus_pid ]]; then
  echo "Stopping Prometheus (PID: $prometheus_pid)..."
  kill $prometheus_pid
  sleep 5
  echo "Prometheus stopped."
fi

# Stop Alertmanager
alertmanager_pid=$(pgrep -f alertmanager)
if [[ -n $alertmanager_pid ]]; then
  echo "Stopping Alertmanager (PID: $alertmanager_pid)..."
  kill $alertmanager_pid
  sleep 5
  echo "Alertmanager stopped."
fi

# Start Prometheus
echo "Starting Prometheus..."
./../prometheus/prometheus --config.file=prometheus/prometheus.yml &
echo "Prometheus started."

# Start Alertmanager
echo "Starting Alertmanager..."
./../alertmanager/alertmanager &
echo "Alertmanager started."

echo "Prometheus and Alertmanager restarted successfully."
