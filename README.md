# MorBus

MorBus is Mobile Morse Communication Device.

You can build own MorBus use a RaspberryPi!

[Demo Video](https://twitter.com/i/status/1366030604186177539)


![キャプションを入力できます](https://pbs.twimg.com/media/EzvQRBQVUAohe6o?format=jpg&name=large)

Build MorBus
===========================

### Parts List:
- RaspberryPi Zero WH
- RaspberryPi Zero HAT PCB
- SD 32GB
- 2x20pin
- OLED Display(SSD1306 128x32)
- LimitSwitch
- SlideSwitch
- TactSwitchx2
- Buzzer
- Lipo Battery 1s 400mAh
- Charge Module

Wiring Parts Like This ->
![キャプションを入力できます](https://camo.elchika.com/64834eb13d8b0e12e089c4aeb70dad33acc116a3/687474703a2f2f73746f726167652e676f6f676c65617069732e636f6d2f656c6368696b612f76312f757365722f33646565346130662d373536372d346638312d396130352d3639353132316531346433652f65393365633639612d643562382d343838332d623061652d623339303632613230636661/) 


Designed with Fusion 360 ->
![キャプションを入力できます](https://camo.elchika.com/db4497b55ba8a92a53d2a2fa9d9f3d3c041cd8c4/687474703a2f2f73746f726167652e676f6f676c65617069732e636f6d2f656c6368696b612f76312f757365722f33646565346130662d373536372d346638312d396130352d3639353132316531346433652f33396238373531662d363333632d346638302d623566322d383431343634333735613365/)

Setup MorBus
===========================

```bash
cd /home/pi
git clone https://github.com/appleuser634/MorBus.git
cd MorBus
```

Activate i2c 

```bash
sudo raspi-config
```

Install Packages
```bash
pip3 install -r requirements.txt
```

Edit message_config.json
```bash
cp message_config_sample.json message_config.json
vim message_config.json
```
