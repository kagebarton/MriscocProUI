import sys
p=sys.argv[1]; s=open(p).read()
old1="""HAL_STEP_TIMER_ISR() {
  #ifndef __AVR__
    // Disable interrupts, to avoid ISR preemption while we reprogram the period
    // (AVR enters the ISR with global interrupts disabled, so no need to do it here)
    hal.isr_off();
  #endif

  HAL_timer_isr_prologue(MF_TIMER_STEP);"""
new1="""HAL_STEP_TIMER_ISR() {
  HAL_timer_isr_prologue(MF_TIMER_STEP);"""
old2="""    static uint32_t ftMotion_nextStepperISR = 0; // Interval until the next FT Motion phase (0 = Now)
  #endif

  // Program timer compare"""
new2="""    static uint32_t ftMotion_nextStepperISR = 0; // Interval until the next FT Motion phase (0 = Now)
  #endif

  #ifndef __AVR__
    // Disable interrupts, to avoid ISR preemption while we reprogram the period
    // (AVR enters the ISR with global interrupts disabled, so no need to do it here)
    hal.isr_off();
  #endif

  // Program timer compare"""
old3="""  // Loop until all events for this ISR have been issued
  do {

    hal_timer_t interval = 0;"""
new3="""  // Loop until all events for this ISR have been issued
  do {
    // Enable ISRs to reduce USART processing latency
    hal.isr_on();

    hal_timer_t interval = 0;"""
old4="""        // Enable ISRs to reduce latency for higher priority ISRs, or all ISRs if no prioritization.
        hal.isr_on();

        // ^== Time critical."""
new4="""        // ^== Time critical."""
for o,n in ((old1,new1),(old2,new2),(old3,new3),(old4,new4)):
    assert s.count(o)==1, o[:60]; s=s.replace(o,n)
open(p,'w').write(s)
