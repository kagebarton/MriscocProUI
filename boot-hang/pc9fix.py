import sys
root=sys.argv[1]
p=root+'/Marlin/src/pins/stm32f1/pins_CREALITY_V4.h'; s=open(p).read()
old="""  #define SDIO_D0_PIN                       PC8
  #define SDIO_D1_PIN                       PC9
  #define SDIO_D2_PIN                       PC10
  #define SDIO_D3_PIN                       PC11
"""
new="""  #define SDIO_D0_PIN                       PC8
  #ifndef TMC_UART_PIN_Y                          // The TMC UART mod wires PC9 (SDIO_D1) to the Y driver, so keep SDIO 1-bit
    #define SDIO_D1_PIN                     PC9
    #define SDIO_D2_PIN                     PC10
    #define SDIO_D3_PIN                     PC11
  #endif
"""
assert s.count(old)==1; open(p,'w').write(s.replace(old,new))
p=root+'/Marlin/src/HAL/STM32/sdio.h'; s=open(p).read()
old="""#define SDIO_D0_PIN   PC8
#define SDIO_D1_PIN   PC9
#define SDIO_D2_PIN   PC10
#define SDIO_D3_PIN   PC11
#define SDIO_CK_PIN   PC12
#define SDIO_CMD_PIN  PD2
"""
new="""// Default pins, unless the pins file defines its own set (leaving out D1-D3 for a 1-bit bus)
#ifndef SDIO_D0_PIN
  #define SDIO_D0_PIN   PC8
  #define SDIO_D1_PIN   PC9
  #define SDIO_D2_PIN   PC10
  #define SDIO_D3_PIN   PC11
  #define SDIO_CK_PIN   PC12
  #define SDIO_CMD_PIN  PD2
#endif
"""
assert s.count(old)==1; open(p,'w').write(s.replace(old,new))
