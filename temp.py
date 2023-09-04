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

SLEEP_AFTER_SECS = 120
current_uptime_secs = 0

pause_update = False


label_clock = M5TextBox(74, 0, "", lcd.FONT_DefaultSmall, 0x32fc04, rotate=90)
label_batt = M5TextBox(60, 0, "", lcd.FONT_DefaultSmall, 0x32fc04, rotate=90)
label_last = M5TextBox(38, 0, "00:00:00", lcd.FONT_DejaVu24, 0xf4ff00, rotate=90)

main_ui = [label_clock, label_batt, label_last]

label_time0 = M5TextBox(6, 10, "17:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time1 = M5TextBox(6, 30, "18:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time2 = M5TextBox(6, 45, "19:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time3 = M5TextBox(6, 60, "21:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label_time4 = M5TextBox(6, 75, "22:00", lcd.FONT_Default, 0xFFFFFF, rotate=0)

times_ui = [label_time0, label_time1, label_time2, label_time3, label_time4]

press_circle = M5Circle(38, 134, 15, 0xf40202, 0xffffff)
press_circle.hide()

banner_bg = M5Rect(0, 130, 80, 30, 0xff04ed, 0xee0afc)
banner_text = M5TextBox(5, 139, "Alfons Timer", lcd.FONT_DefaultSmall, 0xFFFFFF, rotate=0)
banner_ui = [banner_bg, banner_text]


print('Configure wifi')
wifiCfg.autoConnect(lcdShow=True)
print('Get NTP')
ntp = ntptime.client(host='cn.pool.ntp.org', timezone=8)

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

def load_times(max_times=5):
  times = []
  try:
    times = json.loads(open('times.json').read())
  except OSError:
    print('No current file, return empty')
  if len(times) > max_times:
    times = times[-5:]
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

def button_pressed_reset_timer():
  hide_all_ui(banner_ui)
  press_circle.show()
  wait_ms(2000)
  save_time()
  press_circle.hide()
  show_all_ui(banner_ui)

def button_pressed_show_past():
    print('Show past')
    times = load_times()
    global times_ui
    for i in range(5):
        try:
            times_ui[i].setText(get_human_time(times[i]))
        except IndexError:
            times_ui[i].setText('')
    hide_all_ui(main_ui)
    hide_all_ui(banner_ui)
    show_all_ui(times_ui)
    global pause_update
    pause_update = True
    wait_ms(10000)
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


@timerSch.event('seconds')
def tseconds():
  global current_uptime_secs
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
