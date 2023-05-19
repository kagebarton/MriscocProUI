#MAKEFLAGS += -j8

# Set needed variables.
AQUILA_VER ?= GD32
AQUILA_CONFIG_TPL_DIR := configurations/Voxelab\ Aquila
MARLIN_DIR := Marlin
MARLIN_CONFIG_DIR := configurations
MARLIN_REVERT_TO_DEFAULT_CONFIG := true
PLATFORMIO := C:\Users\Andrew\.platformio\penv\Scripts\platformio.exe
PLATFORMIO_FLAGS =
PLATFORMIO_MAIN_DIR := .pio
PLATFORMIO_BUILD_DIR := $(PLATFORMIO_MAIN_DIR)/build
PLATFORMIO_CONF := platformio.ini
GRID ?= 3
FIRMWARE_NAME ?= $(shell date +"firmware-%m%d%Y-%H%M%S")
export FIRMWARE_NAME

# Evaluate HS (High Speed) variable if it's been enabled.
ifeq ($(IS), true)
 DISABLE_IS_X =
 DISABLE_IS_Y =
else
 DISABLE_IS_X = \/\/
 DISABLE_IS_Y = \/\/
endif

# clean:
# 	@echo "Cleaning up..."
# 	rm -rvf $(ALT_BUILD_OUTPUT_DIR)
# 	rm -rvf $(PLATFORMIO_BUILD_DIR)
# 	rm -rvf $(PLATFORMIO_MAIN_DIR)
# .PHONY: clean

Default-NoProbe:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/Default-NP/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/Default-NP/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	cp $(AQUILA_CONFIG_TPL_DIR)/Default-NP/Version.h $(MARLIN_DIR)/Version.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RC_voxelab_maple_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	cp $(MARLIN_DIR)/Version.h $(PLATFORMIO_BUILD_DIR)/Version.h
	C:\Users\Andrew\.platformio\penv\Scripts\platformio.exe run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/Andrew427/Configuration.h $(MARLIN_CONFIG_DIR)/Andrew427/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: Default-NoProbe

BLTouch:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/HC32/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/HC32/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	cp $(AQUILA_CONFIG_TPL_DIR)/HC32/Version.h $(MARLIN_DIR)/Version.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RC_voxelab_maple_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	sed -i 's/#define GRID_MAX_POINTS_X.*/#define GRID_MAX_POINTS_X $(GRID)/g' $(MARLIN_DIR)/Configuration.h
	sed -i 's/[^ ]*#define INPUT_SHAPING_X/$(DISABLE_IS_X)#define INPUT_SHAPING_X/g' Marlin/Configuration_adv.h
	sed -i 's/[^ ]*#define INPUT_SHAPING_Y/$(DISABLE_IS_Y)#define INPUT_SHAPING_Y/g' Marlin/Configuration_adv.h
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	cp $(MARLIN_DIR)/Version.h $(PLATFORMIO_BUILD_DIR)/Version.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/Andrew427/Configuration.h $(MARLIN_CONFIG_DIR)/Andrew427/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: BLTouch

ManualMesh:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/MM/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/MM/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	cp $(AQUILA_CONFIG_TPL_DIR)/MM/Version.h $(MARLIN_DIR)/Version.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RC_voxelab_maple_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	sed -i 's/#define GRID_MAX_POINTS_X.*/#define GRID_MAX_POINTS_X $(GRID)/g' $(MARLIN_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	cp $(MARLIN_DIR)/Version.h $(PLATFORMIO_BUILD_DIR)/Version.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/Andrew427/Configuration.h $(MARLIN_CONFIG_DIR)/Andrew427/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: Manual-Mesh

UBL-BLTouch:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL/Configuration\ Pro.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL/Configuration_adv\ Pro.h $(MARLIN_DIR)/Configuration_adv.h
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL/Version.h $(MARLIN_DIR)/Version.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RC_voxelab_maple_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	sed -i 's/#define GRID_MAX_POINTS_X.*/#define GRID_MAX_POINTS_X $(GRID)/g' $(MARLIN_DIR)/Configuration.h
	sed -i 's/[^ ]*#define INPUT_SHAPING_X/$(DISABLE_IS_X)#define INPUT_SHAPING_X/g' Marlin/Configuration_adv.h
	sed -i 's/[^ ]*#define INPUT_SHAPING_Y/$(DISABLE_IS_Y)#define INPUT_SHAPING_Y/g' Marlin/Configuration_adv.h	
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	cp $(MARLIN_DIR)/Version.h $(PLATFORMIO_BUILD_DIR)/Version.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/Andrew427/Configuration.h $(MARLIN_CONFIG_DIR)/Andrew427/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: UBL-BLTouch

UBL-NoPro:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL/Version.h $(MARLIN_DIR)/Version.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RC_voxelab_maple_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	sed -i 's/#define GRID_MAX_POINTS_X.*/#define GRID_MAX_POINTS_X $(GRID)/g' $(MARLIN_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	cp $(MARLIN_DIR)/Version.h $(PLATFORMIO_BUILD_DIR)/Version.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/Andrew427/Configuration.h $(MARLIN_CONFIG_DIR)/Andrew427/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: UBL-NoPro
