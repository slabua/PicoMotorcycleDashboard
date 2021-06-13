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
![Home](https://lh3.googleusercontent.com/DQQNoy-izvphbdjn8y2N9ZQNjW-PCaRhyFBNDmOKpejVbD1_JEITEXPEs4qgjyogDREKYLBKwL8EthHp6FTP5DquovXFVfcjHINH2klRbMynoErdLQMNl5faEcCTeb4og1xse9lUxe8YeyUnk4hwSaCLnaJBYM_sm9ICkOV1I0r-PBO9hdOsxdbDJBoEa2ZS2CBZwvZmjGBH-12SD8xuaDh0ZZg12_BCSaz8_xaGjGQyGfQfTnl1EhBt_2V4l4wBlMkgsM72zo8C9XtkmkorJZWzkZQGAhZ3KcfczZxIdzdel424rP1P6VMcCIkJ4rEKYGEBFvOBbHKdYFrJi61P9DipMtpHarE2gPcOXp3j7rWquqm9Hvr1AH07typNud06smnfJs9LtqwPJsojwPkG8dp5Qu7fFJMlbRgAF5QKyarkbs-ellsLa-d3FRT5d6Astxy5FPjIS0kw-LyqVi-sbcksmmCJM4HhO5tmRuHdfpujePPObjRV_ylDfSw4PCFjwMDcm-K-JK67aaEfOPbFJx5LIvREsdqiw1glayEeuvPqwaRlO6EyH7_xtxqMCGjEfeg8NUUGgNCNzfxLNg5jSQ7FZbaXfAhqw9wZoenlIfaEBs2nDT5Ze_55l7AlTHMsoy1Jm1c-v-5OubJYLjyyuTtfmRF-y6vy-tXW7i-CLJ8YywF5Vrx1kA6IEGlA4cMKXGHCp_ZA8JXn88HrthRzAkmBHg=s360-no)
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
![Battery](https://lh3.googleusercontent.com/13jAejrSffE4TMIzcMbI9uLHHXhKBIGfGmL3X9DSXrey5v1D_CaSu0KYb2QSnHKgMiyV-buwIBeA_I6uBF0ZP6Uk0khAsLmHOK4eTsUqDxT2A-BgwGkte6zqRRhGwQHX4gJr8LhO95h0QFlFp3NzfkE61bD59ebVFNQgHisr8rDvmZO5X1sfJUgie8AKsZJBgN3OinLi8lQ8u2YQy5nTTTKZO11wDBtE_mc1YPnx4Ul78pvyeQCMDuDasuCPL1H-Y7qZ-kcQObSgxrJrbImPR-HkuxyOOx3u08qd0CVMzcZWeVshrxkElrXX3ruG1ZHI7-p_n1_zUImMWGtRtvrUwPDkXTGFJH3B1VpamGkwB6SPaMc0rl21llrFC1SJr4gd-g5zWFn5h-hHop4W1aFDPR3Sd2boN3xcgJloAIaZ4fduZhUANruoudT9oa27MWJ4k0tWlp2GmAHlPW4HrmXKbNlEbwcfuzQfxO40Xyaud9ngYNhGwoZH5SKqV1uJnwkW76PpzPn3bNeaBzhZinMdvRg7xh8mug_AQLN7EFnTE1PuJIPO8gjpAq3ID9xd4xyTqwbTNcnI8KiQNr9rf-MYDizH4ud3stTBteN0Xyd1GhUgQdBcHqBmIVuPGKHYMoIqoFXrVTplleBYFE3TbtuRgB57HYC-L7W7b2e42SgnmodMlNmnwb7jKtffTzSDDYuOOtJCH3LU3rMOIStRK5nSr86ulA=s360-no)
- A: Go to Home screen
- B: Cycle Brightness presets
- X: Continuous / Discrete battery representation
- Y: Cycle Graphics style
- Y+B: Show Info scroll banner (hold)

### Fuel
![Fuel](https://lh3.googleusercontent.com/GNE1yjpFOPEcio35JUC_gd4xp-zmiilbNXrR9YbfEEQLUw6ca-lA61Ye7dRfE978bOKi-Kve1nG3K4HaV66TYfyOtei8BgixW095J-y3bWSDOYaTv6_E5MwdO86FTvv6ZqBYqunbO5kEOhOCj5VWhs_VM2dsQZFeYEJ8v-RlXaqWDDKOe9UKMsP7b74d4HkYMRlS41mRHd4d05KRq5nITvZf3xo52cjxTXxCJZmJGcZOOfM4RvWBBiGL2c3DMID-l7vgXxKC2RFlE6SSNlqL10kLBgdfRTSdR6o1R5gjDwNtIAguNQaBhLjt508RhcWslyJbOPqeB_E7YIu_JhgPFiRBWdCjw5gXfYXHHlVik6rvEYmRUHsTMsa5tF34GM5XIcm-qkBhrCIZZNiA6RbhPlP0DAcde53nIAvj8OlpzpNTVCUahMKNavSLOqmVik_tI01eHGBfQU1pjq1pDyL0ci1sTBDp584o_EII65aAhlga2Dv95pZgQcpEMMv5EueZeXzK4l2_-mrvV8_YEoqKwiP5NRptWwUUkLK1IRdtKLQNoaIZmGevNm9x-Xvym6eSlIn2voywtBKNwarBXEpsX1Zv62fvO7eIDB2_oyhvVLo1F1LWvCXrv8xETS1bQJPODWXJaaF1pRsdTDVvJzBuvjjCOLUfZKYqeMxlFk8IVJC0iddwnnMxHtcu51zmdOX3uBHjfvOphve02r9zZqS1bZ0Slw=s360-no)
- A: Go to Home screen
- B: Cycle Brightness presets
- X: -
- Y: Cycle Bars style (globally)
- Y+B: Show Info scroll banner (hold)

### Temperature
![Temperature](https://lh3.googleusercontent.com/WN3XFu7HvHHkgJGaWqyb9AQO-0R-LC9s0pcKUvCyuQCj91SU5hOOwuxbqfhi-Ysc10yVHE9k0xlZ3izYcukyn4tYwzyNiunHcEeLb-3LGPM6aoA8NYgSbKO2Bzr_XaZKGr1quXYlnj6x_b-Wy38taLj94MuoeZ9psEUw10O8ntTPBjYSHVm6VA_jQ-0x3H5xWa8hZUw4DReYHbw2KHoSAolCYeve4mljrIqxl90lNZS5g6sBCIeahal1dG73b3sTcl24tk-UH8YihL58lRdD6FddGGjb3Mha_KB92AzPQd-nM-It5CCvyOOkIRCtx3E0TZ4KBiB3Yc6W2NBomE3qThTe9d03QwHTuoFPjcH8eI3R4Ay3RP3_Z7XEKqWDJtya4ECh01If3E92cwG3_pk6I5cRUF9Uy8gy6bNwtJRsw5BeHrQA8FyX5dzKk4Cx2awltV0tqQMrVvG8zb5dFg0neeseX9toGpzOHiVIerGMrBA81Z9WUNmnBQoR9gBcPqUnNhWWAc87vAiEuPnHLRbd0T0ICamoSnMUXrmn4MdK2S-nIstika-viTpoFlO5fYC9-as-UTbZbEmLLLu2h78680hocfxIkGMkBS3j01KE8IIxKxfC5OdZcv5mYt0pkClS4oZH2-aYe4v0Zn7XaHI9GFiUY-OxJYmbo30L2wrA3mfX24nndKhu5GZbx6UGhxABldydy3yhX2yYwuxYmwG8AoS_Zg=s360-no)
- A: Go to Home screen
- B: Cycle Brightness presets
- X: Cycle Temperature sources
- Y: Clear history for the current temperature source
- Y+B: Show Info scroll banner (hold)

### RPM
![RPM](https://lh3.googleusercontent.com/I10MbIm609isX8nLKJVxo3yAVPHpTABvjXPK8sERYc0Y-DjVU9ciQnlVFm4G-tHzH9eBefQi7aaChm8k5k9HbDNG2URIgG7WSL2kBYpacI5ZKW_HGPiYgiyqKYw0xNx_EqxaDyjymaQEMgNis0KKBqkrRSk4A-oxjoT9ea70emWAZfqWQR2ARebld7FMUeCi8dZCyO5CSOxmTHshz5Wib_01LTyAkQXvKWrSJ7c2ZqcO7j3Xnq8oEJnOJzGAsqOOVKeRmuVn4f2UWJGBlP0lVxOZVY2gcTk-SThyPLUewovN0NtS9F4NZjRIJFWCEAXlT6rRpm9EwgTsA5-gcCy-fVez944V9jLCqPFdVqdyC_-Va_4m8m2NzgSQH2FZe2SxBsQSN-MRZ2FKGyS-VmHKEeMJqbvEw6p2Y9K_sCjOVOENRN4n189-RA808QgqxckU4nhYv2jpzb8NZVcRxx4iXX4Qg-0dgYgzharoDCsQoWtx9Z4UkSMFmpAWNd_Zh-ZwPqK5R42GyknLMZcXIv8hI_f4tdWZXS6rj4JWJm2pCd60GJsCWm15-su9EDgq9oA1lgR-yo7Dge-lC9MYrswk-aEDAOE-T63vEVbd6j8wVtgoLapTq6555LY3WvSq0b45JxQDF8rK8WXeo5VqXMOvgOYgav4FCw0mbvoMNC617c_fxmVE7A1krJ2xdndkAvOIOw1c6fQNJap8wcr1foIdsC29ng=s360-no)
- A: Go to Home screen
- B: Cycle Brightness presets
- X: Cycle Ramp style
- Y: Cycle Bars style (globally)
- Y+B: Show Info scroll banner (hold)

### Stats
![Stats](https://lh3.googleusercontent.com/6j1dtjQRWc9Mm4LmAlggXoLZ2Wm1nSbKKiuwRiq-o4nvTfJ-_xMHypEgs8_W4UtBXYzihXH_sFL3NRJ_ko4sQTYhzRal-mwRNovPhI77-YkLzvl4E2dpvnP5iSYub_d7vp-oYyL5UOK8P4EN_NSYrtq02vEZTRgSYw_dwineDWNcrQX7AMp9dbG6dQH8i22g_sCtkSayKp--lZVMsP7WIoFaJYEnBhNpf0IgII61HcI_bxrd-i9CdYAlUjG2l52pYs4O34cjUmWxOZjtUIocnYY9ICPCFhelkUFx9uVhbXNms-nQ1sVhbQ5x1gwiSh6kmRvYsKuibqYFDGMENuhPHe4olV4lTIU3zA4sN3YpnCCKnCFPRtGctt_byBX_E0S8UVT4Gocq-TDyyrji8K0UYx504fkyFRTOQ9zLW6igfThRUhUw8TH3EAJApmexivqah58sB1pcHzZMozhJ9fwYiC5vpf94DujTlPvtuiIqCLv3tiZkQTusmI_02f-szy-FKmQ4VWwmqDo8bpHND1pIklbfgpZuYyHOOsq0xIEZLbP6oubB3Tx5LTKgvBAMUZAW_v1-CyUYiGIp3H6VYXGLg_eBnSmuSfcf3Et7P0iw1e3fwXEx8XOhRWcgmlC_WX099reWQfKVeaCNItRquUtCiE1N0PpJt3hNFvxC8bzU_1fFn8A3LIUIhc2rUIc233y2ti5_d5_jJe2E_82MsjkzbKlPrw=s360-no)
- A: Go to Home screen
- B: Cycle Brightness presets
- X: Update Configuration file
- Y: Reset uptime
- X+B: Reset Configuration file
- Y+B: Show Info scroll banner (hold)
