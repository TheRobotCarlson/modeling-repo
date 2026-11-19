# Electronics

The automated dicer has no custom board: a XIAO ESP32S3, three TMC2209 step/dir
modules (two in parallel on the platen), three servos on a 6 V regulator, and a
24 V supply. Pins are listed at the top of `../firmware/dicer.yaml`. The lid switch
breaks the 24 V to the drivers and servos.
