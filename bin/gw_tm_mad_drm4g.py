#!/usr/bin/env python
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

import sys
import traceback
from argparse import ArgumentParser

from drm4g.core.tm_mad import GwTmMad

def main():
    parser = ArgumentParser(
               description = 'Transfer manager MAD',
               usage       = 'Usage: %(prog)s'
            )
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    options, args = parser.parse_args()
    try:
        GwTmMad().processLine()
    except KeyboardInterrupt:
        sys.exit(-1)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        sys.exit( 'Caught exception: %s: %s' % (e.__class__, str(e)) )

if __name__ == '__main__':
    main()
