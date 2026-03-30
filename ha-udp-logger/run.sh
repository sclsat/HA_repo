#!/usr/bin/env bashio

set -e

CONFIG_PATH=/data/options.json
LOG_DIR=$(bashio::config 'log_dir')
MAX_SIZE_MB=$(bashio::config 'max_size_mb')
ROTATE_COUNT=$(bashio::config 'rotate_count')
LOG_LEVEL=$(bashio::config 'log_level')

bashio::log.info "Запуск UDP Log Collector"
bashio::log.info "Директория логов: ${LOG_DIR}"
bashio::log.info "Максимальный размер: ${MAX_SIZE_MB}MB"
bashio::log.info "Количество ротаций: ${ROTATE_COUNT}"
bashio::log.info "Уровень логирования: ${LOG_LEVEL}"

# Запускаем Python скрипт
exec python3 /udp_logger.py \
    --log-dir "${LOG_DIR}" \
    --max-size-mb "${MAX_SIZE_MB}" \
    --rotate-count "${ROTATE_COUNT}" \
    --log-level "${LOG_LEVEL}"
