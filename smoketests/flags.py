# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration. 
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Package-level global flags are defined here, the rest are defined
where they're used.
"""

from nova import vendor
from gflags import *

# This keeps pylint from barfing on the imports
FLAGS = FLAGS
DEFINE_string = DEFINE_string
DEFINE_integer = DEFINE_integer
DEFINE_bool = DEFINE_bool

# __GLOBAL FLAGS ONLY__
# Define any app-specific flags in their own files, docs at:
# http://code.google.com/p/python-gflags/source/browse/trunk/gflags.py#39
DEFINE_string('admin_access_key', 'admin', 'Access key for admin user')
DEFINE_string('admin_secret_key', 'admin', 'Secret key for admin user')
DEFINE_string('clc_ip', '127.0.0.1', 'IP of cloud controller API')
DEFINE_string('bundle_kernel', 'openwrt-x86-vmlinuz',
              'Local kernel file to use for bundling tests')
DEFINE_string('bundle_image', 'openwrt-x86-ext2.image',
              'Local image file to use for bundling tests')
#DEFINE_string('vpn_image_id', 'ami-CLOUDPIPE',
#                    'AMI for cloudpipe vpn server')

