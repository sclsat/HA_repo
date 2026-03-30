ARG BUILD_FROM
FROM $BUILD_FROM

# Установка Python
RUN apk add --no-cache python3 py3-pip

# Копируем Python скрипт
COPY udp_logger.py /
RUN chmod +x /udp_logger.py

# Используем bashio для логирования
RUN mkdir -p /etc/services.d/udp-logger
COPY run /etc/services.d/udp-logger/run
RUN chmod +x /etc/services.d/udp-logger/run
