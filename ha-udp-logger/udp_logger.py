#!/usr/bin/env python3
import socket
import signal
import sys
import argparse
import logging
import os
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

class UDPLogCollector:
    def __init__(self, log_dir="/share/udp_logs", max_size_mb=10, rotate_count=5, log_level="info"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.port = int(port)
        self.max_size = max_size_mb * 1024 * 1024
        self.rotate_count = rotate_count
        
        self.running = True
        
        # Настройка логирования
        self.setup_logging(log_level)
        
    def setup_logging(self, log_level):
        """Настройка логирования"""
        level = getattr(logging, log_level.upper())
        
        # Лог для UDP сообщений
        self.udp_logger = logging.getLogger('udp')
        self.udp_logger.setLevel(logging.INFO)
        
        # Файловый обработчик с ротацией
        log_file = self.log_dir / 'ha_udp.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_size,
            backupCount=self.rotate_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.udp_logger.addHandler(file_handler)
        
        # Служебный лог
        self.service_logger = logging.getLogger('service')
        self.service_logger.setLevel(level)
        
        # Вывод в консоль (для логов аддона)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.service_logger.addHandler(console_handler)
        
        # Файл со служебными сообщениями
        service_file = self.log_dir / 'collector.log'
        service_handler = RotatingFileHandler(
            service_file,
            maxBytes=5*1024*1024,
            backupCount=3
        )
        service_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.service_logger.addHandler(service_handler)
        
    def signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        self.service_logger.info(f"Received signal {signum}, stopping...")
        self.running = False
        
    def start(self):
        """Запуск сервера"""
        # Устанавливаем обработчики сигналов
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Создаем UDP сокет
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', self.port))
            
            self.service_logger.info(f"UDP server started on port {self.port}")
            self.service_logger.info(f"Logging to: {self.log_dir / 'ha_udp.log'}")
            
        except Exception as e:
            self.service_logger.error(f"Failed to start server: {e}")
            sys.exit(1)
        
        # Статистика
        counter = 0
        last_report = time.time()
        
        # Основной цикл
        while self.running:
            try:
                # Устанавливаем таймаут для возможности проверки self.running
                sock.settimeout(1.0)
                
                # Принимаем данные
                data, addr = sock.recvfrom(65535)
                
                # Декодируем сообщение
                try:
                    message = data.decode('utf-8', errors='ignore').strip()
                except:
                    message = str(data)
                
                # Записываем в лог
                self.udp_logger.info(f"{addr[0]}:{addr[1]} - {message}")
                counter += 1
                
                # Периодический отчет
                now = time.time()
                if now - last_report >= 60:
                    self.service_logger.debug(f"Messages received in last minute: {counter}")
                    counter = 0
                    last_report = now
                    
            except socket.timeout:
                continue
            except Exception as e:
                self.service_logger.error(f"Error receiving data: {e}")
                continue
        
        sock.close()
        self.service_logger.info("UDP server stopped")

def main():
    parser = argparse.ArgumentParser(description='UDP Log Collector')
    parser.add_argument('--log-dir', default='/share/udp_logs')
    parser.add_argument('--max-size-mb', type=int, default=10)
    parser.add_argument('--rotate-count', type=int, default=5)
    parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'])
    parser.add_argument('--port', type=int, default=8881, help='UDP port to listen on')
    
    args = parser.parse_args()
    
    collector = UDPLogCollector(
        log_dir=args.log_dir,
        max_size_mb=args.max_size_mb,
        rotate_count=args.rotate_count,
        log_level=args.log_level,
        port=args.port
    )
    
    collector.start()

if __name__ == "__main__":
    main()
