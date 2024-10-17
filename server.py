import time
import serial
import serial.tools.list_ports


class Server:
    def __init__(self):
        self.received_data = None
        self.ser = None
        self.ports = None

    def connect_port(self, page, received_label):
        try:
            self.ser = serial.Serial(
                port="/dev/ttyTHS1",
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            time.sleep(1)
            self.read_from_port(page, received_label)
        except Exception as e:
            print(f"Error: {e}")

    def close_port(self, label):
        if self.ser and self.ser.is_open:
            self.ser.close()
            # label.config(text="Port Closed")
        # else:
        #     label.config(text="No Port is Open")

    def read_from_port(self, page, received_label):
        if self.ser and self.ser.is_open:
            if self.ser.in_waiting > 0:
                self.received_data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='replace').strip()
                received_label.config(text=f"Received: {self.received_data}")
                page.response_to_request(self.received_data.split())
            page.after(1, lambda: self.read_from_port(page, received_label))

    def send_command(self, command, label):
        if self.ser and self.ser.is_open:
            self.ser.write(command.encode())
            time.sleep(0.002)
            label.config(text=f"Sent: {command.strip()}")

