ARG BUILD_FROM
FROM $BUILD_FROM

# Установка Python
RUN apk add --no-cache python3 py3-pip

# Копируем файлы
COPY udp_logger.py /
COPY run.sh /

RUN chmod +x /run.sh

# Точка входа
CMD ["/run.sh"]
