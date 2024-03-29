#
# Copyright 2021 Santander Meteorology Group (UC-CSIC)
#
# Licensed under the EUPL, Version 1.1 only (the
# "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
#

"""
Restart DRM4G's daemon deleting all the jobs available on DRM4G.

Usage:
    drm4g clear [ options ]

Options:
   -d --debug    Debug mode.
"""

from time                 import sleep
from drm4g                import console_logger
from drm4g.commands       import Daemon

def run( arg ) :
    try:
        daemon = Daemon()
        daemon.stop()
        sleep( 2.0 )
        daemon.clear()
    except Exception as err :
        console_logger.error( str( err ) )
