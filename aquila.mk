# Set needed variables.
AQUILA_VER ?= G32
AQUILA_CONFIG_TPL_DIR := config/aquila_templates
MARLIN_DIR := Marlin
MARLIN_CONFIG_DIR := config
MARLIN_REVERT_TO_DEFAULT_CONFIG := true
PLATFORMIO := pio
PLATFORMIO_FLAGS =
PLATFORMIO_MAIN_DIR := .pio
PLATFORMIO_BUILD_DIR := $(PLATFORMIO_MAIN_DIR)/build
PLATFORMIO_CONF := platformio.ini
GRID ?= 3
FIRMWARE_NAME ?= $(shell date +"firmware-%m%d%Y-%H%M%S")
export FIRMWARE_NAME

# Evaluate HS (High Speed) variable if it's been enabled.
ifeq ($(IS), true)
 DISABLE_HS_BLTOUCH =
else
 DISABLE_HS_BLTOUCH = \/\/
endif

clean:
	@echo "Cleaning up..."
	rm -rvf $(ALT_BUILD_OUTPUT_DIR)
	rm -rvf $(PLATFORMIO_BUILD_DIR)
	rm -rvf $(PLATFORMIO_MAIN_DIR)
.PHONY: clean

Default-NoProbe:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/Default-NoProbe/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/Default-NoProbe/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RET6_voxelab_aquila_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/default/Configuration.h $(MARLIN_CONFIG_DIR)/default/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: Default-NoProbe

BLTouch:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/BLTouch-3x3/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/BLTouch-3x3/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RET6_voxelab_aquila_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	sed -i 's/#define GRID_MAX_POINTS_X.*/#define GRID_MAX_POINTS_X $(GRID)/g' $(MARLIN_DIR)/Configuration.h
	sed -i 's/[^ ]*#define BLTOUCH_HS_MODE/$(DISABLE_HS_BLTOUCH)#define BLTOUCH_HS_MODE/g' Marlin/Configuration_adv.h
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/default/Configuration.h $(MARLIN_CONFIG_DIR)/default/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: BLTouch

ManualMesh:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/ManualMesh-3x3/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/ManualMesh-3x3/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RET6_voxelab_aquila_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	sed -i 's/#define GRID_MAX_POINTS_X.*/#define GRID_MAX_POINTS_X $(GRID)/g' $(MARLIN_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/default/Configuration.h $(MARLIN_CONFIG_DIR)/default/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: Manual-Mesh

UBL-BLTouch:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL-BLTouch-10x10/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL-BLTouch-10x10/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RET6_voxelab_aquila_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	sed -i 's/#define GRID_MAX_POINTS_X.*/#define GRID_MAX_POINTS_X $(GRID)/g' $(MARLIN_DIR)/Configuration.h
	sed -i 's/[^ ]*#define BLTOUCH_HS_MODE/$(DISABLE_HS_BLTOUCH)#define BLTOUCH_HS_MODE/g' Marlin/Configuration_adv.h
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/default/Configuration.h $(MARLIN_CONFIG_DIR)/default/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: UBL-BLTouch

UBL-NoProbe:
	mkdir -p $(PLATFORMIO_BUILD_DIR)
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL-NoProbe-3x3/Configuration.h $(MARLIN_DIR)/Configuration.h
	cp $(AQUILA_CONFIG_TPL_DIR)/UBL-NoProbe-3x3/Configuration_adv.h $(MARLIN_DIR)/Configuration_adv.h
	sed -i 's/default_envs =.*/default_envs = STM32F103RET6_voxelab_aquila_$(AQUILA_VER)/g' $(PLATFORMIO_CONF)
	sed -i 's/#define GRID_MAX_POINTS_X.*/#define GRID_MAX_POINTS_X $(GRID)/g' $(MARLIN_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration.h  $(PLATFORMIO_BUILD_DIR)/Configuration.h
	cp $(MARLIN_DIR)/Configuration_adv.h $(PLATFORMIO_BUILD_DIR)/Configuration_adv.h
	FIMWARE_NAME=$(FIRMWARE_NAME) $(PLATFORMIO) run $(PLATFORMIO_FLAGS)
	@echo ""
	@echo "Post processing cleanup..."
	@echo ""
	if $(MARLIN_REVERT_TO_DEFAULT_CONFIG); then cp -v $(MARLIN_CONFIG_DIR)/default/Configuration.h $(MARLIN_CONFIG_DIR)/default/Configuration_adv.h $(MARLIN_DIR); fi
.PHONY: UBL-NoProbe
