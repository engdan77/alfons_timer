# Alfons Timer

## Background

On 22nd of August 2023 we got a new born son named Alfons, as most parent might have experienced this journey of feeding baby with pacifier in the middle of the night can make one it hard to remember when the baby last time was fed. So I looked in my box and found this [M5StickC](https://shop.m5stack.com/products/stick-c) which is an awesome piece considering the size based on an [ESP32](https://en.wikipedia.org/wiki/ESP32) and including battery and display. And thought I could have good use of a portable "smart" timer that could <u>keep track of when last time baby was fed and keep record of those last times</u>, so this led me to put some Micropython code into this device named **Alfons Timer**.

## Installation

I flashed the device using the [M5 Burner](https://docs.m5stack.com/en/download), that assures all those libraries being there, and I also used web based [UI Flow](https://flow.m5stack.com/) to simplify building the UI. At this stage you also configure the device to connect to your Wifi.

Also using the [M5-stack Visual Code plugin](https://marketplace.visualstudio.com/items?itemName=curdeveryday.vscode-m5stack-mpy) made it easier to upload `temp.py` and `umail.py`to the device, so since there is a default `temp.py`that you can ovewrite with the one in this source.

### Pre-configure e-mail

Upload file `wifi.json` with content such as

```json
{
  "ssid": "MYWIFI"
  "password": "WIFIPASSWORD"
}
```



#### Have last time records sent as e-mail

In such case register a gmail account with its app password and upload a file `email.json`with content such as

```json
{
 "sender_email": "ME@gmail.com", 
 "sender_name": "ME", 
 "sender_app_password": "MYAPPPASSWORD", 
 "recipient_email": "daniel@engvalls.eu"
}
```



## Technical notes behind the code

To allow this to function consider this device does not come with a [RTC](https://en.wikipedia.org/wiki/Real-time_clock) allowing it to keep track of time when it is being powered off, we have in within the code so that it initially connects to Internet and collects the time using [NTP](https://sv.wikipedia.org/wiki/Network_Time_Protocol). Then the time series are stored as JSON within its own flash memory.

## How to use

Once you start the device you click once on **Button A** at the initial logo, then it allows you to go to **Apps** and select `temp` .. so it will start next time you start the device.

Within the App you can click on **Button A** for saving a record of time, and you have a yellow timer that states how long time ago the baby was fed. With the **Button B** you are able to see the last 5 records.

In the view with those times you can press **Button A** to enable power saver mode, including deep sleep after 2 minutes idle.



## Screenshot and demo

You also have a video at https://youtu.be/ZL6n6SZF8e8

<img src="https://raw.githubusercontent.com/engdan77/project_images/master/pics/image-20230904150626358.png" alt="image-20230904150626358" style="zoom: 33%;" />

