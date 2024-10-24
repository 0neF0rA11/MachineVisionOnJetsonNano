# Программа машинного зрения для Jetson Nano developer Kit

# Инструкция по установке ПО на Jetson Nano
1. Установите ОС на jetson nano с официального сайта [Nvidia](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit)  
2. При первом запуске обязательно обновите систему
```bash
sudo apt update && sudo apt upgrade
sudp apt autoremove
```
3. Установите python 3.8 (его не нужно компилировать)
```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.8
python3.8 --version
```
4. Настройте виртуальное окружение
```bash
sudo apt-get install python3.8-venv
python3.8 -m venv myenv
source myenv/bin/activate
sudo apt-get install python3-pip
```
5. Клонируйте репозиторий
```bash
git clone https://github.com/0neF0rA11/MachineVisionOnJetsonNano.git
cd MachineVisionOnJetsonNano/
```
6. Установите зависимости
```bash
sudo pip install --upgrade pip
pip install -r requirements.txt
```
## Настройка UART
1. Освобободите UART 
```bash
sudo systemctl stop nvgetty
sudo systemctl disable nvgetty
sudo udevadm trigger
sudo reboot
```
2. Настройте права доступа вашему пользователю
```bash
sudo usermod -aG dialout $USER
```
Подключите USB to TTL  переходник по инструкции RX к TX, TX к RX, GND к GND. Распиновку можно найти [тут](https://jetsonhacks.com/nvidia-jetson-nano-2gb-j6-gpio-header-pinout/)
## Настройка запуска 
1. Создадайте `start.sh` файл запуска
```bash
sudo nano ~/start.sh
```  
2. Вставьте код:
```bash
#!/bin/bash

source myenv/bin/activate
cd MachineVisionOnJetsonNano/
python3 GUI.py
```
3. Настройте права на исполнение
```bash
sudo chmod +x ./start.sh
```
4. Чтобы запустить программу используйте
```bash
./start.sh
```
## Создание иконки запуска на рабочем столе
1. Создайте `MachineVision.desktop`
```bash
sudo nano ~/Desktop/MachineVision.desktop
```  
2. Вставьте код. Не забудьте изменить `user` на имя своего пользователя
```bash
[Desktop Entry]
Type=Application
Name=Vision
Exec=/home/user/start.sh
Path=/home/user/
Icon=/home/user/MachineVisionOnJetsonNano/images_data/application_icon.png
Terminal=false
```
3. Настройте права доступа
```bash
sudo chmod +x ~/Desktop/MachineVision.desktop
```
4. Измените владельца файла на себя
```bash
sudo chown user:user ~/Desktop/MachineVision.desktop
```
