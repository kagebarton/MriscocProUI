MEMORY
{
  ram (rwx) : ORIGIN = 0x20000000, LENGTH = 128K - 40
  rom (rx)  : ORIGIN = 0x08007000, LENGTH = 512K - 64K
}
/* (STM32F411RET6 / N32G455REL7) ram is set to 128K, even though it may be technically 144K for N32, F_CPU speed can also be 100mhz or 144mhz for N32 TODO: create a .json variant board for this specfic chip*/
/* Provide memory region aliases for common.inc */
REGION_ALIAS("REGION_TEXT", rom);
REGION_ALIAS("REGION_DATA", ram);
REGION_ALIAS("REGION_BSS", ram);
REGION_ALIAS("REGION_RODATA", rom);

/* Let common.inc handle the real work. */
INCLUDE common.inc
