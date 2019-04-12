import time
import board
import gc
import json
import neopixel
import displayio
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.Label import Label
import adafruit_touchscreen

try:
    from secrets import secrets
except ImportError:
    print("""Wifi SSID/Password, Darksky key, location and other information
    is kept in secrets.py.  Please edit and review that file.""")
    raise


def format_date(t):
    days = ["Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    month = months[t.tm_mon - 1]
    day = days[t.tm_wday]
    d = day + ", " + month + " " + str(t.tm_mday) + ", " + str(t.tm_year)
    return d


def pixel_around():
    for p in range(0, 59):
        pixels[p] = (0, 0, 0)
        pixels[p+1] = (0, 255, 0)
        pixels.show()
    pixels[59] = (0, 0, 0)
    pixels.show()


ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      calibration=((7000, 59600),
                                                   (8000, 57100)),
                                      size=(320, 240))

pixels = neopixel.NeoPixel(board.D4, 60, brightness=.8, auto_write=False)
pixels.fill((0, 0, 0))
pixels.show()

# Set up where we'll be fetching data from
DARKSKY_API = "https://api.darksky.net/forecast/%s/%g,%g?units=us&lang=en&exclude=minutely,hourly,alerts,flags"  # NOQA

darksky = DARKSKY_API % (secrets.get('darksky_key', 'KEYMISSING'),
                         secrets.get('latitude', 0),
                         secrets.get('longitude', 0)
                         )
# the current working directory (where this file is)
cwd = ("/"+__file__).rsplit('/', 1)[0]
pyportal = PyPortal(url=darksky,
                    json_path=[],
                    status_neopixel=board.NEOPIXEL,
                    default_bg=cwd+"/pyportal_startup.bmp"
                    )


last_weather = 0
last_time = 0
last_flip = 0

pixel_around()

pyportal.set_background(cwd+"/pyportal_startup2.bmp")

pages = []

pp = displayio.Group(max_size=10, x=0, y=0)
pages.append(pp)
page = 0

preload = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-!,.%_ "\'?!\u00b0' # NOQA

font1 = bitmap_font.load_font(cwd+"/fonts/Anton-Regular-30.bdf")
font1.load_glyphs(preload)
font1_height = font1.get_bounding_box()[1]

date_label = Label(font1,
                   max_glyphs=30,
                   color=0xbbbbff,
                   x=160,
                   y=int(font1_height/2)+20)
pp.append(date_label)

current_label = Label(font1,
                      max_glyphs=30,
                      color=0xbbbbff,
                      x=20,
                      y=210)
pp.append(current_label)

yy = 90
temp_label = Label(font1,
                   max_glyphs=10,
                   color=0xbbbbff,
                   x=0,
                   y=yy)
pp.append(temp_label)
yy += font1_height + 5

humid_label = Label(font1,
                    max_glyphs=10,
                    color=0xbbbbff,
                    x=0,
                    y=yy)
pp.append(humid_label)
yy += font1_height + 5

press_label = Label(font1,
                    max_glyphs=10,
                    color=0xbbbbff,
                    x=0,
                    y=yy)
pp.append(press_label)
yy += font1_height + 5


icon_font_map = ["clear-day",
                 "clear-night",
                 "rain",
                 "snow",
                 "sleet",
                 "wind",
                 "fog",
                 "cloudy",
                 "partly-cloudy-day",
                 "partly-cloudy-night",
                 "thunderstorm",
                 "hail",
                 "tornado"
                 ]

icon_font_glyphs = b"BCRXWFLNHI'()*+\\G6"

font3 = bitmap_font.load_font(cwd+"/fonts/Meteocons-120.bdf")
font3.load_glyphs(icon_font_glyphs)

icon_label = Label(font3,
                   max_glyphs=1,
                   color=0xbbbbff,
                   x=20,
                   y=160)
pp.append(icon_label)

pyportal.splash.append(pp)

pp = displayio.Group(max_size=10)
pages.append(pp)

desc_label = Label(font1,
                   max_glyphs=200,
                   color=0xbbbbff,
                   x=0,
                   y=120)
pp.append(desc_label)

pixel_around()

pyportal.get_local_time()
last_time = time.monotonic()


pyportal.set_background(cwd+"/background.bmp")
date_label.text = "Almost Ready..."
date_label.x = 160 - int(date_label.bounding_box[2] / 2)

pixel_around()

prior_day = 0
prior_sec = 0
prior_hpixel = 0
prior_mpixel = 0
prior_spixel = 0

while True:
    if (time.monotonic() - last_time) > 3600:
        last_time = time.monotonic()
        pyportal.get_local_time()
        gc.collect()

    if (time.monotonic() - last_weather) > 900 or last_weather == 0:
        last_weather = time.monotonic()
        value = pyportal.fetch()
        # print("Weather Response", value)
        data = json.loads(value)
        value = None
        gc.collect()
        current_label.text = data["currently"]["summary"]
        # current_label.x = 160 - int(current_label.bounding_box[2] / 2)
        icon = data["currently"]["icon"]
        i = -1
        for ic in icon_font_map:
            i += 1
            if icon_font_map[i] == icon:
                c = icon_font_glyphs[i]
                icon_label.text = chr(c)
        temp_label.text = u"%.1f\u00b0F" % data["currently"]["temperature"]
        temp_label.x = 300 - temp_label.bounding_box[2]
        humid_label.text = u"%.0f%%" % (data["currently"]["humidity"]*100)
        humid_label.x = 300 - humid_label.bounding_box[2]
        press_label.text = u"%.2finHg" % (data["currently"]["pressure"] *
                                          0.02952998751 + 1.07)
        press_label.x = 300 - press_label.bounding_box[2]
        gc.collect()
        desc = data["daily"]["summary"]
        desc = pyportal.wrap_nicely(desc, 24)
        desc_label.text = '\n'.join(desc)
        desc_label.x = 160 - int(desc_label.bounding_box[2] / 2)
        gc.collect()
        print("Free memory", gc.mem_free())

    if prior_sec != time.localtime().tm_sec:
        t = time.localtime()
        prior_sec = t.tm_sec
        if prior_day != t.tm_mday:
            d = format_date(t)
            prior_day = t.tm_mday
            print(d)
            date_label.text = d
            date_label.x = 160 - int(date_label.bounding_box[2] / 2)
        gc.collect()
        poffset = 8
        hpixel = t.tm_hour % 12 * 5
        hpixel += int(t.tm_min / 12)
        mpixel = t.tm_min
        spixel = t.tm_sec
        hpixel += 8
        hpixel %= 60
        mpixel += 8
        mpixel %= 60
        spixel += 8
        spixel %= 60
        pixels[prior_hpixel] = (0, 0, 0)
        pixels[prior_mpixel] = (0, 0, 0)
        pixels[prior_spixel] = (0, 0, 0)
        pixels[hpixel] = (255, 0, 0)
        (r, g, b) = pixels[mpixel]
        g = 255
        pixels[mpixel] = (r, g, b)
        (r, g, b) = pixels[spixel]
        b = 255
        pixels[spixel] = (r, g, b)
        pixels.show()
        prior_hpixel = hpixel
        prior_mpixel = mpixel
        prior_spixel = spixel
        gc.collect()

    pt = ts.touch_point
    if pt:
        pyportal.splash.pop()
        page += 1
        if page >= len(pages):
            page = 0
        pyportal.splash.append(pages[page])

    gc.collect()
    time.sleep(.05)
