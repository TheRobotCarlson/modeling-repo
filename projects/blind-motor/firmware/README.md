# Firmware

ESPHome configs for the worm-gear shade motors (XIAO ESP32-C6, DRV8833, JGY-370 with
encoder). Copy `secrets.yaml` from `../../ha-remote/firmware/` (same Wi-Fi and key) or
fill in `secrets.example.yaml`, set `static_ip` in each shade's file, then:

    esphome config shade-1.yaml
    esphome run shade-1.yaml      # first time over USB, then over Wi-Fi

Calibrate: hold the box's down button to fully closed, press **Set closed here** in
Home Assistant; hold up to fully open, press **Set open here**. See the site's Home
Assistant page.

Passes `esphome config` (2026.10.2) apart from the placeholder API key. Not compiled or
run on hardware.
