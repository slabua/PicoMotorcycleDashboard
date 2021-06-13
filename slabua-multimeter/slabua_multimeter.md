# MultiMeter (DRAFT)

### A Digital MultiMeter based on the [Raspberry Pi Pico](https://www.raspberrypi.org/products/raspberry-pi-pico/) and the [Pimoroni Pico Display Pack](https://shop.pimoroni.com/products/pico-display-pack), for motorcycle monitoring purposes.

## Components
- Raspberry Pi Pico
  - Main control board
- Pico Display Pack
  - Input:
    - Button A
    - Button B
    - Button X
    - Button Y
  - Output:
    - 240x135 px IPS display
    - RGB LED
- Sensors
  - DS18B20 Temperature sensor

## Wiring Diagram
TODO

---
## Usage

## Screens
- [Home](#Home)
- [Battery](#Battery)
- [Fuel](#Fuel)
- [Temperature](#Temperature)
- [RPM](#RPM)
- [STATS](#STATS)

### Home
- A: Go to next (Battery) screen
  - If pressed again within 3 seconds,  
    cycle through all the screens
- B: Cycle Brightness presets
- X: Select Multiple or Single Temperature mode
- Y: If Multiple (*) or Single (**) Temperature mode:
  - Cycle Temperature sources (**)
  - Cycle bars style (*) (globally)
- X+B: Cycle Colour palette
- Y+B: Show Info scroll banner (hold)

### Battery
- A: Go to Home screen
- B: Cycle Brightness presets
- X: Continuous / Discrete battery representation
- Y: Cycle Graphics style
- Y+B: Show Info scroll banner (hold)

### Fuel
- A: Go to Home screen
- B: Cycle Brightness presets
- X: -
- Y: Cycle Bars style (globally)
- Y+B: Show Info scroll banner (hold)

### Temperature
- A: Go to Home screen
- B: Cycle Brightness presets
- X: Cycle Temperature sources
- Y: Clear history for the current temperature source
- Y+B: Show Info scroll banner (hold)

### RPM
- A: Go to Home screen
- B: Cycle Brightness presets
- X: Cycle Ramp style
- Y: Cycle Bars style (globally)
- Y+B: Show Info scroll banner (hold)

### Stats
- A: Go to Home screen
- B: Cycle Brightness presets
- X: Update Configuration file
- Y: Reset uptime
- X+B: Reset Configuration file
- Y+B: Show Info scroll banner (hold)
