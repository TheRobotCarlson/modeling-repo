"""Power budget: what one press costs, and how long a charge lasts.

The remote spends almost all its life in deep sleep. A press wakes the ESP32-S3,
which either joins Wi-Fi and tells Home Assistant over the native API, or sends
one LoRa packet to a gateway that is always on. Then it sleeps again.

Every current below is an estimate (EST) or a published figure (SOURCE); none is
measured yet. The measure page says how to check them with a USB power meter.
"""

import math

import numpy as np

from modelkit import save_series

CAPACITY_MAH = 350.0      # SOURCE: Adafruit 2750
USABLE = 0.85             # stop at ~3.5 V to keep the cell healthy

# --- asleep, in microamps ---------------------------------------------------------
SLEEP_UA = {
    "xiao_deep_sleep": 14.0,      # SOURCE: Seeed wiki, XIAO ESP32S3 deep sleep at 3.8 V
    "sx1262_sleep": 0.6,          # SOURCE: ESPHome sx126x docs, sleep after set_mode_sleep
    "sense_divider": 2.4,         # 1M + (1M || 2.2M) across ~4 V; the 2.2M is the USB sense
    "accelerometer": 2.0,         # SOURCE: MSA311 datasheet, low-power mode, typ. Puck only:
                                  # the bar has none and sleeps 2 uA lower.
    "cell_protection": 3.0,       # EST: typical protection IC on the cell
    "self_discharge": CAPACITY_MAH * 0.03 / 730 * 1000,   # EST: 3 %/month, as an equivalent current
}
SX1262_STANDBY_UA = 600.0         # EST: radio left in standby (never told to sleep)

# --- one press, as (seconds, milliamps) phases --------------------------------------
WIFI_PRESS = [
    ("boot", 0.35, 45),           # EST: ROM + bootloader + ESPHome setup
    ("join Wi-Fi", 1.0, 110),     # EST: fast_connect + static IP, no DHCP
    ("API + event", 1.2, 90),     # EST: Home Assistant connects, event fired
    ("buzz", 0.12, 90 + 60),      # feedback: motor on 3V3, 60 mA at 3 V (SOURCE: Adafruit 1201)
    ("linger", 0.38, 90),         # the LED stays lit (~2 mA, EST, left out) as the event leaves
]

# The puck wakes when it is moved, joins Wi-Fi and waits idle_window (4 s from boot)
# for a press. A pick-up without a press costs this much.
MOTION_WAKE = [
    ("boot", 0.35, 45),
    ("join Wi-Fi", 1.0, 110),
    ("wait for a press", 3.0, 90),
]


def lora_airtime(sf=7, bw=125e3, payload=6, preamble=8, cr=1, implicit=True, crc=True):
    """Semtech AN1200.13 time-on-air, seconds."""
    t_sym = 2 ** sf / bw
    de = 1 if t_sym > 16e-3 else 0
    n = 8 + max(math.ceil((8 * payload - 4 * sf + 28 + 16 * crc - 20 * implicit) / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (preamble + 4.25) * t_sym + n * t_sym


AIRTIME = lora_airtime()
LORA_PRESS = [
    ("boot", 0.35, 45),           # EST: same boot, no Wi-Fi at all
    ("radio setup", 0.05, 45),    # EST
    ("transmit", AIRTIME, 45 + 45),   # EST: ~45 mA radio at +14 dBm, plus the ESP32
    ("buzz", 0.12, 45 + 60),
    ("blink", 0.2, 45),
    ("sleep the radio", 0.02, 45),
]


def charge_mah(phases):
    return sum(t * ma for _, t, ma in phases) / 3600


def timeline(phases, t):
    out = np.zeros_like(t)
    t0 = 0.0
    for _, dt, ma in phases:
        out[(t >= t0) & (t < t0 + dt)] = ma
        t0 += dt
    return out


sleep_ua = sum(SLEEP_UA.values())
per_day_sleep = sleep_ua * 24 / 1000                       # mAh/day
wifi_mah, lora_mah = charge_mah(WIFI_PRESS), charge_mah(LORA_PRESS)

# --- chart 1: one press -------------------------------------------------------------
t = np.round(np.arange(0, 3.4, 0.01), 3)
save_series(
    "ha-remote", "press", t,
    {"Wi-Fi": timeline(WIFI_PRESS, t), "LoRa": timeline(LORA_PRESS, t)},
    title="Current drawn by one press, from wake to sleep",
    x_label="time after the press (s)", y_label="current (mA)",
    params={"wifi_awake_s": round(sum(p[1] for p in WIFI_PRESS), 2),
            "wifi_charge_per_press_mAh": round(wifi_mah, 4),
            "lora_awake_s": round(sum(p[1] for p in LORA_PRESS), 2),
            "lora_airtime_ms": round(AIRTIME * 1000, 1),
            "lora_charge_per_press_mAh": round(lora_mah, 4),
            "wifi_to_lora_ratio": round(wifi_mah / lora_mah, 1)},
)

# --- chart 2: days per charge -------------------------------------------------------
presses = np.arange(1, 101)
usable = CAPACITY_MAH * USABLE


def days(per_press, sleep_per_day=per_day_sleep):
    return usable / (sleep_per_day + presses * per_press)


trap = (sleep_ua - SLEEP_UA["sx1262_sleep"] + SX1262_STANDBY_UA) * 24 / 1000
save_series(
    "ha-remote", "life", presses,
    {"LoRa": days(lora_mah), "Wi-Fi": days(wifi_mah), "Wi-Fi, radio never put to sleep": days(wifi_mah, trap)},
    title="Days between charges, by presses per day",
    x_label="presses per day", y_label="days per charge",
    params={"battery_mAh": CAPACITY_MAH, "usable_fraction": USABLE,
            "sleep_current_uA": round(sleep_ua, 1),
            **{f"sleep_{k}_uA": round(v, 2) for k, v in SLEEP_UA.items()},
            "sleep_only_days": round(usable / per_day_sleep),
            "wifi_10_per_day_days": round(float(days(wifi_mah)[9])),
            "lora_10_per_day_days": round(float(days(lora_mah)[9])),
            "radio_left_in_standby_days": round(float(days(wifi_mah, trap)[9])),
            "motion_wake_mAh": round(charge_mah(MOTION_WAKE), 3),
            "wifi_10_presses_10_pickups_days": round(float(days(wifi_mah, per_day_sleep + 10 * charge_mah(MOTION_WAKE))[9]))},
)

# --- chart 3: the optional sensor module ---------------------------------------------
# A separate kit with an SHT40, waking on a timer to report temperature and humidity.
# Same sleep as a remote, minus the USB sense and accelerometer; the sensor board is
# powered from a GPIO only while it measures, so it adds nothing asleep.
SENSOR_SLEEP_UA = (SLEEP_UA["xiao_deep_sleep"] + SLEEP_UA["sx1262_sleep"] + 2.0
                   + SLEEP_UA["cell_protection"] + SLEEP_UA["self_discharge"])
SENSOR_READ = [("power the sensor and read", 0.02, 45 + 0.4)]   # SHT40 high precision: ~10 ms (EST)
WIFI_REPORT = [p for p in WIFI_PRESS if p[0] != "buzz"] + SENSOR_READ
LORA_REPORT = [p for p in LORA_PRESS if p[0] not in ("buzz", "blink")] + SENSOR_READ
minutes = np.arange(5, 61, 1)
per_day_sensor = SENSOR_SLEEP_UA * 24 / 1000


def sensor_days(phases):
    return usable / (per_day_sensor + (24 * 60 / minutes) * charge_mah(phases))


wifi_s, lora_s = sensor_days(WIFI_REPORT), sensor_days(LORA_REPORT)
at = lambda arr, m: round(float(arr[minutes == m][0]))
save_series(
    "ha-remote", "sensor", minutes,
    {"LoRa": lora_s, "Wi-Fi": wifi_s},
    title="Sensor module: days between charges, by minutes between reports",
    x_label="minutes between reports", y_label="days per charge",
    params={"battery_mAh": CAPACITY_MAH, "sleep_current_uA": round(SENSOR_SLEEP_UA, 1),
            "wifi_report_mAh": round(charge_mah(WIFI_REPORT), 4),
            "lora_report_mAh": round(charge_mah(LORA_REPORT), 4),
            "wifi_every_10_min_days": at(wifi_s, 10), "lora_every_10_min_days": at(lora_s, 10),
            "wifi_every_30_min_days": at(wifi_s, 30), "lora_every_30_min_days": at(lora_s, 30)},
)
