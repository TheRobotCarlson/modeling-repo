#pragma once
// ESPHome's ext1 wake on the ESP32-S3 does not set any pulls on the wake pins, and
// the digital pull-ups switch off in deep sleep, so the pins would float. Keep the
// RTC domain powered and turn on its pull-ups instead. Called from on_shutdown.
#include <initializer_list>
#include "driver/rtc_io.h"
#include "esp_sleep.h"

namespace rtc_pullups {
inline void enable(std::initializer_list<int> pins) {
  esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_ON);
  for (int p : pins) {
    auto g = static_cast<gpio_num_t>(p);
    rtc_gpio_init(g);
    rtc_gpio_set_direction(g, RTC_GPIO_MODE_INPUT_ONLY);
    rtc_gpio_pulldown_dis(g);
    rtc_gpio_pullup_en(g);
  }
}
}  // namespace rtc_pullups
