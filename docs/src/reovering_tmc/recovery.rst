
.. _`Recovering TMC Low`:

How to recover TMC Low when it remains in given ObsState for long time
=======================================================================
The following table demonstrates the steps to recover TMC Low from the ObsState it is currently stuck in.
The provided steps consist of command-line instructions that are executable from any terminal environment.


Using Abort() Command
---------------------
+-----------------------------------+------------------------------------------------------------------------+ 
| Scenario                          |               Steps to recover                                         | 
+===================================+========================================================================+ 
| When TMC Low stuck in             |- Using Subarray Node                                                   |
| one of the ObsState while running |    - Create device proxy of subarray node                              |
|                                   |    - To recover TMC Low stuck in RESOURCING from Subarray node execute:|
|                                   |      Abort() command followed by Restart() command.                    |
|                                   |                                                                        |
| + RESOURCING                      |      - subarray_node.Abort()                                           |
|                                   |      - subarray_node.Restart()                                         |
| + CONFIGURING                     |                                                                        |
+-----------------------------------+------------------------------------------------------------------------+   

Using ReleaseAllResources() command
------------------------------------

When TMC Low AssignResources() command executed on some of the devices successfully and TMC subarray goes in
RESOURCING due to one of the device gets stuck in RESOURCING.
So instead of doing Abort and Restart, invoke ReleaseAllResources() command on the subarray where the ObsState 
is IDLE.
and on the device where the obsState is RESOURCING invoke Abort() command followed by Restart() command.


+-----------------------------------+------------------------------------------------------------------------+ 
| Scenario                          |               Steps to recover                                         | 
+===================================+========================================================================+ 
| When TMC Low stuck in RESOURCING  | - Create device proxy of cspleafnode, sdpleafnode and mccsleafnode     |
|                                   | - Check the ObsState of each device                                    |
|                                   | - If the ObsState of the device is IDLE, invoke ReleaseAllResources()  |
|                                   |   command on that device. For Ex.                                      |
|                                   |                                                                        |
|                                   | - To check ObsState of cspleafnode, execute                            |
|                                   |   `cspleafnode_proxy.obsState`                                         |
|                                   | - To release resources of the device, execute                          |
|                                   |   `cspleafnode_proxy.ReleaseAllResources()`                            |
|                                   | - To recover the device in RESOURCING obsState, execute                |
|                                   |   Abort() command followed by Restart() command                        |
|                                   | - `stuck_device_proxy.Abort()`                                         |
|                                   | - `stuck_device_proxy.Restart()`                                       |
+-----------------------------------+------------------------------------------------------------------------+ 

TMC Low in FAULT ObsState
-------------------------
+-----------------------------------+------------------------------------------------------------------------+ 
| Scenario                          |               Steps to recover                                         | 
+===================================+========================================================================+ 
| When TMC Low stuck in FAULT       |- Using Subarray Node                                                   |
| ObsState                          |    - Create device proxy of subarray node                              |
|                                   |    - To recover TMC Low stuck in FAULT from Subarray node execute:     |
|                                   |      RESTART command.                                                  |
|                                   |    - subarray_node.Restart()                                           |
+-----------------------------------+------------------------------------------------------------------------+
