import time

import tango
from tango import DeviceProxy

from tests.resources.test_harness.constant import mccs_subarraybeam

from .central_node_low import CentralNodeWrapperLow
from .subarray_node_low import SubarrayNodeWrapperLow


class TMCLow:
    def __init__(self):
        """Set all devices proxy required for TMC"""
        self.central_node = CentralNodeWrapperLow()
        self.subarray_node = SubarrayNodeWrapperLow()
        self.deleted_device = {}
        self.device_deleted_flag = False  # Flag to indicate device deletion

    def delete_device_from_db(self, server_type):
        if server_type == "MCCS_SUBARRAYBEAM":
            self.mccs_subarraybeam = DeviceProxy(mccs_subarraybeam)
            self.mccs_subarraybeam_server = DeviceProxy(
                f"dserver/{self.mccs_subarraybeam.info().server_id}"
            )
            db = tango.Database()
            # Delete mccs subarraybeam Device
            db.delete_device(self.mccs_subarraybeam)
            self.deleted_device[mccs_subarraybeam] = {
                "device_name": mccs_subarraybeam,
                "server_name": "MccsSubarrayBeam/subarraybeam-01",
                "class_name": "MccsSubarrayBeam",
            }
            self.device_deleted_flag = True  # Set flag when device is deleted

    def add_device_to_db(
        self, device_name: str, class_name: str, server_name: str
    ):
        """Add Device to DB"""
        db = tango.Database()
        dev_info = tango.DbDevInfo()
        dev_info.name = device_name
        dev_info._class = class_name
        dev_info.server = server_name
        db.add_device(dev_info)

    def RestartServer(self, server_type: str):
        """Restart server based on provided server type"""
        if server_type == "MCCS_SUBARRAYBEAM":
            self.mccs_subarraybeam_server.RestartServer()
        time.sleep(3)

    def tear_down(self):
        """Tear down"""
        self.central_node.tear_down()
        if self.device_deleted_flag:  # Check if device deletion flag is set
            # Add device back to the database
            for _, device_info in self.deleted_device.items():
                self.add_device_to_db(
                    device_info["device_name"],
                    device_info["class_name"],
                    device_info["server_name"],
                )

        # Reset the flag after tear down
        self.device_deleted_flag = False

    def TelescopeOn(self):
        """Execute TelescopeOn command"""
        self.central_node.move_to_on()
