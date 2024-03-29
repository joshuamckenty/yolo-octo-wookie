..
      Copyright 2010 United States Government as represented by the
      Administrator of the National Aeronautics and Space Administration. 
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Volume Documentation
====================
                           
Nova uses ata-over-ethernet (AoE) to export storage volumes from multiple storage nodes. These AoE exports are attached (using libvirt) directly to running instances.

Nova volumes are exported over the primary system VLAN (usually VLAN 1), and not over individual VLANs.

AoE exports are numbered according to a "shelf and blade" syntax. In order to avoid collisions, we currently perform an AoE-discover of existing exports, and then grab the next unused number. (This obviously has race condition problems, and should be replaced by allocating a shelf-id to each storage node.)

The underlying volumes are LVM logical volumes, created on demand within a single large volume group. 


The :mod:`storage` Module
-------------------------

.. automodule:: nova.volume.storage
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`storage_unittest` Module
----------------------------------

.. automodule:: nova.tests.storage_unittest
    :members:
    :undoc-members:
    :show-inheritance:

