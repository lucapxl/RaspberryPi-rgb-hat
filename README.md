# python script and service unit for Raspberry PI RGB Cooling HAT

This code works for the Yahboom Raspberrpi PI RGB Cooling HAT with oled display <https://category.yahboom.net/products/rgb-cooling-hat>

It's a modified version of the original code <https://github.com/YahboomTechnology/Raspberry-Pi-RGB-Cooling-HAT>.

## Install

This script depends on some python ```Adafruit``` libraries that can be installed with the following command

```bash
sudo pip3 install Adafruit_BBIO Adafruit-GPIO Adafruit-PureIO Adafruit-SSD1306
```

## Config

edit rgb-hat.service

```conf
[Service]
ExecStart=/usr/bin/python3 -u rgb-hat.py    # Make sure the name of the file is correct
WorkingDirectory=/home/pi/rgb-hat           # Replace this with the actual script location
```

copy or 'ln -s' the rgb-hat.service file into ```/etc/systemd/system/```

```bash
# Either
sudo cp rgb-cooling-hat.py /etc/systemd/system/
# ... OR
sudo ln -s /home/pi/rgb-hat/rgb-hat.service /etc/systemd/system/
```

## Usage

To Start and Stop the service use

```bash
# Start
sudo systemctl start rgb-hat.service
# Stop
sudo systemctl stop rgb-hat.service
```

To enable/disable auto start of service during boot

```bash
# Enable auto start
sudo systemctl enable rgb-hat.service
# Disable auto start
sudo systemctl disable rgb-hat.service
```
