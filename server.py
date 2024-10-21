import time
import serial
import logging
import os


LOG_FILE = 'server_log.txt'
MAX_LOG_LINES = 100

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def manage_log_file():
    """Удаление старых строк, если количество строк в логе превышает MAX_LOG_LINES."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()

        if len(lines) > MAX_LOG_LINES:
            with open(LOG_FILE, 'w') as f:
                f.writelines(lines[-MAX_LOG_LINES:])


class Server:
    def __init__(self):
        self.received_data = None
        self.ser = None
        self.ports = None

    def connect_port(self, page):
        try:
            self.ser = serial.Serial(
                port="/dev/ttyTHS1",
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            time.sleep(1)
            logging.info("Подключение к порту /dev/ttyTHS1 успешно установлено.")
            self.read_from_port(page)
        except Exception as e:
            logging.error(f"Ошибка при подключении к порту: {e}")
        manage_log_file()

    def close_port(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("Порт был закрыт.")
        else:
            logging.warning("Попытка закрыть порт, который не был открыт.")
        manage_log_file()

    def read_from_port(self, page):
        if self.ser and self.ser.is_open:
            if self.ser.in_waiting > 0:
                try:
                    self.received_data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='replace').strip()
                    logging.info(f"Получены данные: {self.received_data}")
                    page.response_to_request(self.received_data.split())
                except Exception as e:
                    logging.error(f"Ошибка при чтении данных: {e}")
                manage_log_file()
            page.after(1, lambda: self.read_from_port(page))

    def send_command(self, command):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(command.encode())
                time.sleep(0.002)
                logging.info(f"Отправлены данные: {command.strip()}")
            except Exception as e:
                logging.error(f"Ошибка при отправке команды: {e}")
        else:
            logging.warning("Попытка отправки команды через закрытый порт.")
        manage_log_file()
