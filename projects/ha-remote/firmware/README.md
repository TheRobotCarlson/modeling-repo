# Firmware

ESPHome configs. Copy `secrets.example.yaml` to `secrets.yaml` and fill it in, set
`static_ip` in each remote's file, then:

    esphome run puck.yaml      # or bar.yaml, gateway.yaml

The first flash is over USB-C. After that, a remote only listens for updates while
`input_boolean.remotes_stay_awake` is on in Home Assistant.

Checked with ESPHome 2026.10.2: all configs pass `esphome config`, and puck (Wi-Fi),
bar (LoRa) and gateway build with `esphome compile`. Not yet run on hardware.
