#!/usr/bin/with-contenv bashio

set -e

# Читаем конфигурацию
CONFIG_PATH=/data/options.json
LOG_DIR=$(bashio::config 'log_dir')
MAX_SIZE_MB=$(bashio::config 'max_size_mb')
ROTATE_COUNT=$(bashio::config 'rotate_count')
LOG_LEVEL=$(bashio::config 'log_level')

# Создаем директорию для логов
mkdir -p "${LOG_DIR}"

# Выводим информацию
bashio::log.info "========================================="
bashio::log.info "UDP Log Collector Starting..."
bashio::log.info "Log directory: ${LOG_DIR}"
bashio::log.info "Max size: ${MAX_SIZE_MB}MB"
bashio::log.info "Rotate count: ${ROTATE_COUNT}"
bashio::log.info "Log level: ${LOG_LEVEL}"
bashio::log.info "========================================="

# Запускаем Python скрипт
exec python3 /udp_logger.py \
    --log-dir "${LOG_DIR}" \
    --max-size-mb "${MAX_SIZE_MB}" \
    --rotate-count "${ROTATE_COUNT}" \
    --log-level "${LOG_LEVEL}"
