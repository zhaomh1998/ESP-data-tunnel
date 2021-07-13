echo Install SiLabs Driver from: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers!
read -p "Press enter to confirm"

mkdir temp
cd temp
# http://micropython.org/download/esp8266/
curl http://micropython.org/resources/firmware/esp8266-20200911-v1.13.bin --output firmware.bin

sudo pip install esptool
sudo pip install mpfshell

echo Erasing Flash
esptool.py erase_flash

echo Flasing firmware
esptool.py --baud 460800 write_flash --flash_size=4MB 0 firmware.bin

cd ..
rm -r temp

mpfshell -c "open cu.SLAB_USBtoUART"