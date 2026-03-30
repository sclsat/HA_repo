ARG BUILD_FROM
FROM $BUILD_FROM

# Установка Python если его нет
RUN apk add --no-cache python3 py3-pip

# Копируем файлы
COPY run.sh /
COPY udp_logger.py /
RUN chmod a+x /run.sh

# Команда запуска
CMD [ "/run.sh" ]
