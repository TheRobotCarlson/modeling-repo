# Firmware

ESPHome configs for the bead-chain shade motors. Copy `secrets.yaml` from
`../../ha-remote/firmware/` (same Wi-Fi and key) or fill in `secrets.example.yaml`, set
`static_ip` in each shade's file, then:

    esphome config shade-1.yaml
    esphome run shade-1.yaml      # first time over USB, then over Wi-Fi

Calibrate from Home Assistant: shade fully down, **Set closed here**; then **Open**,
**Nudge up/down** to the top, **Set open here**. See the site's Home Assistant page.

Adapted from github.com/jamesrklau/bead-chain-blind-motor (MIT). Not yet run on hardware.
