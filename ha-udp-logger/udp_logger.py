#!/usr/bin/env python3
import socket
import signal
import sys
import argparse
import logging
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

class UDPLogCollector:
    def __init__(self, log_dir="/data/logs", max_size_mb=10, rotate_count=5, log_level="info"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.port = 8881
        self.max_size = max_size_mb * 1024 * 1024
        self.rotate_count = rotate_count
        
        self.running = True
        self.socket = None
        
        # Настройка логирования
        self.setup_logging(log_level)
        
    def setup_logging(self, log_level):
        """Настройка системы логирования"""
        level = getattr(logging, log_level.upper())
        
        # Лог для UDP сообщений
        self.udp_logger = logging.getLogger('udp_logger')
        self.udp_logger.setLevel(logging.DEBUG)
        
        log_file = self.log_dir / 'ha_udp.log'
        handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_size,
            backupCount=self.rotate_count,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.udp_logger.addHandler(handler)
        
        # Служебный лог
        self.service_logger = logging.getLogger('service')
        self.service_logger.setLevel(level)
        
        # Консольный вывод
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.service_logger.addHandler(console_handler)
        
        # Файловый лог
        service_log_file = self.log_dir / 'collector.log'
        service_handler = RotatingFileHandler(
            service_log_file,
            maxBytes=5*1024*1024,
            backupCount=3
        )
        service_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.service_logger.addHandler(service_handler)
        
    def handle_signal(self, signum, frame):
        """Обработка сигналов"""
        self.service_logger.info(f"Получен сигнал {signum}, остановка...")
        self.running = False
        if self.socket:
            self.socket.close()
        sys.exit(0)
    
    def start(self):
        """Запуск коллектора"""
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            
            self.service_logger.info(f"Коллектор запущен на порту {self.port}")
            self.service_logger.info(f"Логи пишутся в: {self.log_dir / 'ha_udp.log'}")
            
        except Exception as e:
            self.service_logger.error(f"Ошибка: {e}")
            sys.exit(1)
        
        # Основной цикл
        while self.running:
            try:
                self.socket.settimeout(1.0)
                data, addr = self.socket.recvfrom(65535)
                message = data.decode('utf-8', errors='ignore').strip()
                self.udp_logger.info(f"{addr[0]}:{addr[1]} - {message}")
            except socket.timeout:
                continue
            except Exception as e:
                self.service_logger.error(f"Ошибка приема: {e}")
                
        self.service_logger.info("Коллектор остановлен")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-dir', default='/data/logs')
    parser.add_argument('--max-size-mb', type=int, default=10)
    parser.add_argument('--rotate-count', type=int, default=5)
    parser.add_argument('--log-level', default='info')
    
    args = parser.parse_args()
    
    collector = UDPLogCollector(
        log_dir=args.log_dir,
        max_size_mb=args.max_size_mb,
        rotate_count=args.rotate_count,
        log_level=args.log_level
    )
    
    collector.start()

if __name__ == "__main__":
    main()
