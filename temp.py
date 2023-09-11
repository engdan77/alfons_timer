from m5stack import *
from m5ui import *
from uiflow import *
import machine
import utime
import wifiCfg
import ntptime
import time
import wifiCfg
import json
import time

SLEEP_AFTER_SECS = 120
current_uptime_secs = 0
power_save = False
pause_update = False


label_clock = M5TextBox(74, 0, "", lcd.FONT_DefaultSmall, 0x32fc04, rotate=90)
label_batt = M5TextBox(60, 0, "", lcd.FONT_DefaultSmall, 0x32fc04, rotate=90)
label_last = M5TextBox(38, 0, "00:00:00", lcd.FONT_DejaVu24, 0xf4ff00, rotate=90)

main_ui = [label_clock, label_batt, label_last]
for _ in main_ui:
   _.hide()

label_time0 = M5TextBox(6, 15, "00:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time1 = M5TextBox(6, 30, "00:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time2 = M5TextBox(6, 45, "00:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time3 = M5TextBox(6, 60, "00:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time4 = M5TextBox(6, 75, "00:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time5 = M5TextBox(6, 90, "00:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time6 = M5TextBox(6, 105, "00:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_power_mode = M5TextBox(5, 139, "", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=0)
label_power_mode.hide()

times_ui = [label_time0, label_time1, label_time2, label_time3, label_time4, label_time5, label_time6]
for _ in times_ui:
   _.hide()

press_circle = M5Circle(38, 134, 15, 0xf40202, 0xffffff)
press_circle.hide()

banner_bg = M5Rect(0, 130, 80, 30, 0xff04ed, 0xee0afc)
banner_text = M5TextBox(5, 139, "Alfons Timer", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=0)
banner_ui = [banner_bg, banner_text]
lcd.clear()


def wifi_connect():
  # New
  print("start connect wifi")
  try:
     print('Found wifi configuration')
     c = json.loads(open('wifi.json').read())
  except OSError:
     print('No wifi.cfg use default wifi configuration')
     wifiCfg.autoConnect(lcdShow=True)
     return
  print('Connecting to ', c['ssid'])
  for i in range(1,10):
      if not (wifiCfg.wlan_sta.isconnected()):
          lcd.clear()
          lcd.setCursor(10, 10)
          lcd.print('Attempt {}'.format(i))
          print("try reconnect attempt ", i)
          r = wifiCfg.connect(c['ssid'], c['password'], 5000, block=True)
          print('Wifi result: ', r)
          wait(5 * i)
      else:
         print('Connected')
         break
      print("get ifconfig")
      print(wifiCfg.wlan_sta.ifconfig())
      wait(1)
  else:
      print('Failed connect to wifi')
      lcd.clear()
      lcd.setCursor(10, 10)
      lcd.print('Fail')
      wait(5)
      machine.reset()

    
  
def get_time():
  print('Get NTP')
  ntp = ntptime.client(host='cn.pool.ntp.org', timezone=8)
  return ntp

wifi_connect()
ntp = get_time()
watchdog = machine.WDT(timeout=30000)
lcd.clear()


def hide_all_ui(input_list):
  for _ in input_list:
    _.hide()

def show_all_ui(input_list):
  for _ in input_list:
    _.show()

def zpad(text):
    if len(str(text)) == 1:
        return '0{}'.format(text)
    else:
        return str(text)

def get_timestamp():
    return ntp.getTimestamp() - (3600 * 6)

def get_human_date():
    n = get_timestamp()
    year, month, day, _ = time.localtime(n)
    return '{}-{}-{}'.format(year, zpad(month), zpad(day))

def get_human_time(ts=None):
    if not ts:
        n = get_timestamp()
    else:
        n = ts
    _, _, _, hour, minute, second, _, _ = time.localtime(n)
    return '{}:{}:{}'.format(zpad(hour), zpad(minute), zpad(second))

def time_diff_human(seconds):
  current = get_timestamp()
  seconds = current - seconds
  hours = int(seconds / 3600)
  minutes = int((int(seconds) - (hours * 3600)) / 60)
  seconds = int(seconds) - (hours * 3600) - (minutes * 60)
  r = '{}:{}:{}'.format(zpad(hours), zpad(minutes), zpad(seconds))
  return r

def load_times(max_times=7):
  times = []
  try:
    times = json.loads(open('times.json').read())
  except OSError:
    print('No current file, return empty')
  if len(times) > max_times:
    times = times[-max_times:]
  return times

def save_time():
  print('Saving time')
  current_ts = get_timestamp()
  print('Saving time:', str(current_ts))
  times = load_times()
  times.append(current_ts)
  f = open('times.json', 'w')
  f.write(json.dumps(times))
  print('Closing file')
  f.close()

def time_since_human():
  times = load_times()
  last_time = None
  if not times:
    print('No time already stored so using current')
    last_time = get_timestamp()
  else:
    print('Getting last time')
    last_time = times[-1]
  time_diff = time_diff_human(last_time)
  return time_diff

def last_times_as_text():
    texts = []
    print('Get past as texts')
    times = load_times()
    print('Times found ', times)
    global times_ui
    for i in range(7):
        try:
            texts.append(get_human_time(times[i]))
        except IndexError:
            pass
    return texts

def button_pressed_reset_timer():
  hide_all_ui(banner_ui)
  press_circle.show()
  wait_ms(2000)
  save_time()
  press_circle.hide()
  show_all_ui(banner_ui)
  # Send as email if enabled
  times = last_times_as_text()
  times_text = '\n'.join(times)
  times_text = times_text.replace(':', '.')
  print('Sending times ', times_text)
  send_email('Alfons sista napptider', times_text)


def button_pressed_show_past():
    print('Show past')
    times = load_times()
    global times_ui
    for i in range(7):
        try:
            times_ui[i].setText(get_human_time(times[i]))
        except IndexError:
            times_ui[i].setText('')
    hide_all_ui(main_ui)
    hide_all_ui(banner_ui)
    show_all_ui(times_ui)
    global pause_update
    pause_update = True
    global power_save
    for _ in range(100):
        if btnA.isPressed():
            power_save = not power_save
            label_power_mode.setText('Bat. spar {}'.format({True: 'ja', False: 'nej'}[power_save]))
            label_power_mode.show()
            wait_ms(1000)
            label_power_mode.hide()
        wait_ms(100)
    hide_all_ui(times_ui)
    show_all_ui(main_ui)
    show_all_ui(banner_ui)
    pause_update = False


def get_battery():
  volt = axp.getBatVoltage()
  print('Current volt: ', volt)
  if volt < 3.20: return -1
  if volt < 3.27: return 0
  if volt < 3.61: return 5
  if volt < 3.69: return 10
  if volt < 3.71: return 15
  if volt < 3.73: return 20
  if volt < 3.75: return 25
  if volt < 3.77: return 30
  if volt < 3.79: return 35
  if volt < 3.80: return 40
  if volt < 3.82: return 45
  if volt < 3.84: return 50
  if volt < 3.85: return 55
  if volt < 3.87: return 60
  if volt < 3.91: return 65
  if volt < 3.95: return 70
  if volt < 3.98: return 75
  if volt < 4.02: return 80
  if volt < 4.08: return 85
  if volt < 4.11: return 90
  if volt < 4.15: return 95
  if volt < 4.20: return 100
  if volt >= 4.20: return 101

def turn_off_display():
    lcd.clear()
    axp._regChar(0x28, ((20 & 0x0f) << 4))

def deep_sleep():
    p37 = machine.Pin(37, mode = machine.Pin.IN, pull = machine.Pin.PULL_UP)
    p37.irq(trigger = machine.Pin.WAKE_LOW, wake = machine.DEEPSLEEP)
    machine.deepsleep(172800000)

def get_email_config():
    required_keys = ('sender_email', 'sender_name', 'sender_app_password', 'recipient_email')
    try:
        email_config = json.loads(open('email.json').read())
        print('Read email config', email_config)
    except OSError:
        print('Unable to read email.json')
        return None
    if not all([item for item in email_config.keys()]):
        print('Failed get all keys ', required_keys)
        return None
    return email_config


def send_email(email_subject, email_body):
    c = get_email_config()
    if not c:
        print('No valid email skipping')
        return
    import umail
    # email_body = '02:44:18,12:28:11,15:10:19,15:13:10,15:16:29,15:20:53,15:24:49\n\n'
    for to_address in c['recipient_email'].split(','):
      print('Sending email to ', to_address)
      smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True) # Gmail's SSL port
      smtp.login(c['sender_email'], c['sender_app_password'])
      smtp.to(to_address)
      smtp.write("From:" + c['sender_name'] + "<"+ c['sender_email'] +">\n")
      smtp.write("Subject:" + email_subject + "\n")
      print('Within send_email send body: ', email_body)
      smtp.write(email_body)
      smtp.send()
      smtp.quit()

def update_display():
    t = get_human_time()
    print('Current time: ', t)
    global label_clock
    label_clock.setText('Tid: {}'.format(t,))
    label_batt.setText('Batteri: {}%'.format(get_battery()))
    global label_last
    time_since = time_since_human()
    print('Time since last: ', time_since)
    label_last.setText(str(time_since))
    global watchdog
    watchdog.feed()


@timerSch.event('seconds')
def tseconds():
  global current_uptime_secs
  if power_save:
    current_uptime_secs += 1
    if current_uptime_secs >= SLEEP_AFTER_SECS:
        print('Going to sleep')
        turn_off_display()
        deep_sleep()
  global pause_update
  if not pause_update:
    update_display()

def main():
    print('Current time:', ntp.getTimestamp())
    print('starting timer')
    timerSch.run('seconds', 1000, 0x00)
    hide_all_ui(times_ui)
    show_all_ui(main_ui)
    show_all_ui(banner_ui)
    while True:
      wait_ms(10)
      if btnA.isPressed():
        button_pressed_reset_timer()
        wait_ms(3000)
      if btnB.isPressed():
        button_pressed_show_past()
main()