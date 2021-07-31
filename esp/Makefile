# Credit https://github.com/mmphego/uPython-Plant-Irrigation-System/blob/master/Makefile
######################################################################
# User configuration
######################################################################

# Linux Debian/Ubuntu

# Serial port
PORT=cu.SLAB_*
SPEED=460800

# Path to programs
MPFSHELL=mpfshell
ESPTOOL=esptool.py
FIRMWARE=./firmware.bin
# Get latest version from http://www.micropython.org/download#esp8266
FIRMWAREVERSION=esp8266-20200911-v1.13.bin

######################################################################
# End of user config
######################################################################
PORTS=$(shell ls /dev/${PORT})
PORTS_NOPATH=$(notdir $(PORTS))
#FILES=$(notdir $(shell ls *.py))


.PHONY: erase # : Erase flash on chip
erase:
	$(ESPTOOL) --port /dev/$(PORT) erase_flash
	@sleep 5


.PHONY: flash # : Upload new firmware to chip
flash: firmware
	$(ESPTOOL) --port /dev/$(PORT) --baud $(SPEED) write_flash --flash_size=detect 0 $(FIRMWARE)
	@sleep 10
	@echo 'Power cycle the device'


.PHONY: reset # : Hard reset chip
reset:
	for p in $(PORTS_NOPATH); do \
		echo Resetting $$p; \
		$(MPFSHELL) --open $$p --reset -n; \
	done


.PHONY: install
install:
	@bash -c "if ! command -v esptool.py >/dev/null 2>&1; then python3 -m pip install --user -U esptool;fi"
	@bash -c "if ! command -v mpfshell >/dev/null 2>&1; then python3 -m pip install --user -U mpfshell;fi"


.PHONY: firmware # : Download latest firmware from http://www.micropython.org/download#esp8266
firmware: install
	@echo Go to https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers and install SiLabs USB driver!
	@read -p "Press enter to confirm the driver has been installed correctly"
	@bash -c "[ -f $(FIRMWARE) ] || curl http://micropython.org/resources/firmware/$(FIRMWAREVERSION) --output $(FIRMWARE)"


.PHONY: upload # : Upload *.py to all boards
upload:
	@for p in $(PORTS_NOPATH); do \
  		echo Uploading to $$p; \
  		$(MPFSHELL) --open $$p -nc "mput .*\.py"; \
	done

.PHONY: check # : Compile Python code
check:
	python3 -m py_compile *.py
	rm -rf __pycache__
	rm -f *.pyc

.PHONY: repl # : Open repl on chip
repl:
	for p in $(PORTS_NOPATH); do \
		$(MPFSHELL) --open $$p -nc repl; \
	done

.PHONY: all # :Bootstrap ie erase, flash, and upload
all: install erase flash check upload clean

.PHONY: help # : Please use \`make <target>' where <target> is one of
help:
	@grep '^.PHONY: .* #' Makefile | sed 's/\.PHONY: \(.*\) # \(.*\)/\1 \2/' | expand -t20

.PHONY: clean
clean:
	rm -rf $(FIRMWARE)
	rm -rf *.pyc
