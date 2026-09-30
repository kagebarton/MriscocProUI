/**
 * Boot-hang tracer (diagnostic only, not for upstream).
 *
 * RAM-neutral: no static or global variables, so the .data/.bss layout is
 * identical to the untraced build. Output goes straight to USART1 by polling.
 *
 * - boottrace_tick(), called from HAL_SYSTICK_Callback: once 8 s have passed
 *   without setup() reaching MF_RUNNING, every 2 s print the interrupted PC,
 *   LR, xPSR and the code addresses found on the interrupted stack.
 * - Fault handlers: print the fault frame and fault status registers every
 *   ~2 s forever, refreshing the IWDG so the report keeps repeating.
 */
#include "../platforms.h"

#ifdef HAL_STM32

#include "../../inc/MarlinConfig.h"
#include "../../MarlinCore.h"

extern "C" uint32_t _estack;

#define BT_FLASH_LO 0x08007000UL
#define BT_FLASH_HI 0x08080000UL

static inline bool bt_is_code(const uint32_t v) {
  return (v & 1) && v >= BT_FLASH_LO && v < BT_FLASH_HI;
}

static void bt_uart_ready() {
  if (USART1->CR1 & USART_CR1_UE) return;       // Already set up by MYSERIAL1.begin()
  RCC->APB2ENR |= RCC_APB2ENR_USART1EN | RCC_APB2ENR_IOPAEN | RCC_APB2ENR_AFIOEN;
  GPIOA->CRH = (GPIOA->CRH & ~(0xFUL << 4)) | (0xBUL << 4); // PA9 AF push-pull 50 MHz
  USART1->BRR = SystemCoreClock / BAUDRATE;
  USART1->CR1 = USART_CR1_UE | USART_CR1_TE;
}

static void bt_putc(const char c) {
  while (!(USART1->SR & USART_SR_TXE)) { /* wait */ }
  USART1->DR = uint8_t(c);
}

static void bt_puts(const char *s) { while (*s) bt_putc(*s++); }

static void bt_hex(const uint32_t v) {
  for (int8_t i = 28; i >= 0; i -= 4) bt_putc("0123456789abcdef"[(v >> i) & 0xF]);
}

static void bt_kv(const char *k, const uint32_t v) { bt_puts(k); bt_hex(v); }

// Print up to 'maxn' Thumb return addresses found in the words above 'sp'
static void bt_stack_code(const uint32_t *sp, uint8_t maxn) {
  bt_puts(" ra:");
  const uint32_t *top = &_estack;
  for (uint8_t i = 0; i < 160 && sp < top && maxn; ++i, ++sp)
    if (bt_is_code(*sp)) { bt_putc(' '); bt_hex(*sp); --maxn; }
}

extern "C" void boottrace_tick() {
  const uint32_t t = HAL_GetTick();
  if (t < 8000 || (t % 2000) || Marlin::isRunning()) return;

  // Find SysTick_Handler's saved EXC_RETURN; the hardware frame starts above it.
  const uint32_t *sp = (const uint32_t *)__get_MSP();
  const uint32_t *frame = nullptr;
  uint32_t exc = 0;
  for (uint8_t i = 0; i < 48; ++i) {
    const uint32_t v = sp[i];
    if (v == 0xFFFFFFF9UL || v == 0xFFFFFFF1UL || v == 0xFFFFFFFDUL) { exc = v; frame = &sp[i + 1]; break; }
  }

  bt_uart_ready();
  bt_kv("\r\nBT t=", t);
  bt_kv(" st=", uint32_t(Marlin::state));
  if (!frame) { bt_puts(" noframe\r\n"); return; }
  bt_kv(" pc=", frame[6]);
  bt_kv(" lr=", frame[5]);
  bt_kv(" psr=", frame[7]);
  bt_kv(" exc=", exc);
  const uint32_t *isp = frame + 8 + ((frame[7] >> 9) & 1);
  bt_kv(" sp=", uint32_t(isp));
  bt_stack_code(isp, 16);
  bt_puts("\r\n");
}

extern "C" void boottrace_fault(const uint32_t *frame, const uint32_t exc) {
  __disable_irq();
  bt_uart_ready();
  for (;;) {
    bt_kv("\r\nFAULT ipsr=", __get_IPSR());
    bt_kv(" pc=", frame[6]);
    bt_kv(" lr=", frame[5]);
    bt_kv(" psr=", frame[7]);
    bt_kv(" exc=", exc);
    bt_kv(" cfsr=", SCB->CFSR);
    bt_kv(" hfsr=", SCB->HFSR);
    bt_kv(" mmfar=", SCB->MMFAR);
    bt_kv(" bfar=", SCB->BFAR);
    bt_kv(" sp=", uint32_t(frame));
    bt_kv(" st=", uint32_t(Marlin::state));
    bt_stack_code(frame + 8, 16);
    bt_puts("\r\n");
    for (volatile uint32_t n = 0; n < 12000000UL; ++n) IWDG->KR = 0xAAAA;
  }
}

extern "C" __attribute__((naked)) void HardFault_Handler() {
  __asm volatile(
    " tst lr, #4      \n"
    " ite eq          \n"
    " mrseq r0, msp   \n"
    " mrsne r0, psp   \n"
    " mov r1, lr      \n"
    " b boottrace_fault \n"
  );
}
extern "C" void MemManage_Handler()  __attribute__((naked, alias("HardFault_Handler")));
extern "C" void BusFault_Handler()   __attribute__((naked, alias("HardFault_Handler")));
extern "C" void UsageFault_Handler() __attribute__((naked, alias("HardFault_Handler")));

#endif // HAL_STM32
