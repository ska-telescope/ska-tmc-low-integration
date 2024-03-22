import tango
import time
mccs_controller = "low-mccs/control/control"
controller = tango.DeviceProxy(mccs_controller)
db = tango.Database()
pasd_bus_trls = db.get_device_exported("low-mccs/pasdbus/*")
for pasd_bus_trl in pasd_bus_trls:
    pasdbus = tango.DeviceProxy(pasd_bus_trl)
    if pasdbus.adminmode != 0:
        pasdbus.adminmode = 0
        time.sleep(0.1)

device_trls = db.get_device_exported("low-mccs/*")
devices = []
for device_trl in device_trls:
    if "daq" in device_trl or "calibrationstore" in device_trl:
        continue
    device = tango.DeviceProxy(device_trl)
    if device.adminmode != 0:
        device.adminmode = 0
        devices.append(device)
        time.sleep(0.1)