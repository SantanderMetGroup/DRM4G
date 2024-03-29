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
import logging
from drm4g.core.configure  import Configuration
from drm4g.utils.message   import Send


class GwImMad (object):
    """
    Information manager MAD

    The format to send a request to the Information MAD, through its standard input, is:

        OPERATION HID HOST ARGS

    Where:
    -OPERATION: Can be one of the following:
        -INIT: Initializes the MAD (i.e. INIT - - -).
        -DISCOVER: Discovers hosts (i.e. DISCOVER - - - ).
        -MONITOR: Monitors a host (i.e. MONITOR HID HOST -).
        -FINALIZE: Finalizes the MAD (i.e. FINALIZE - - -).
    -HID: if the operation is MONITOR, it is a host identifier, chosen by GridWay. Otherwise it is ignored.
    -HOST: If the operation is MONITOR it specifies the host to monitor. Otherwise it is ignored.

    The format to receive a response from the MAD, through its standard output, is:

        OPERATION HID RESULT INFO

    Where:
    -OPERATION: Is the operation specified in the request that originated the response.
    -HID: It is the host identifier, as provided in the submission request.
    -RESULT: It is the result of the operation. Could be SUCCESS or FAILURE.
    -INFO: If RESULT is FAILURE, it contains the cause of failure. Otherwise, if OPERATION
        is   DISCOVER, it contains a list of discovered host, or if OPERATION is MONITOR,
        it contains a list of host attributes.
    """

    logger  = logging.getLogger(__name__)
    message = Send()

    def __init__(self):
        self._resources  = dict()
        self._config     = None

    def do_INIT(self, args):
        """
        Initializes the MAD (i.e. INIT - - -)
        @param args : arguments of operation
        @type args : string
        """
        out = 'INIT - SUCCESS -'
        self.message.stdout(out)
        self.logger.debug(out)

    def do_DISCOVER(self, args, output=True):
        """
        Discovers hosts (i.e. DISCOVER - - -)
        @param args : arguments of operation
        @type args : string
        """
        OPERATION, HID, HOST, ARGS = args.split()
        try:
            self._config  = Configuration()
            self._config.load()
            errors        = self._config.check()
            assert not errors, ' '.join( errors )

            self._resources  = self._config.make_resources()
            communicators    = self._config.make_communicators()
            hosts = ""
            for resname in sorted( self._resources.keys() ) :
                if  self._config.resources[ resname ][ 'enable' ].lower()  == 'false' :
                    continue
                if  'cloud_provider' in self._config.resources[ resname ].keys():
                    continue
                try :
                    self._resources[ resname ][ 'Resource' ].Communicator = communicators[ resname ]
                    self._resources[ resname ][ 'Resource' ].Communicator.connect()
                    hosts = hosts + " " + self._resources[ resname ] [ 'Resource' ].hosts()
                    self._resources[ resname ][ 'Resource' ].Communicator.close()
                except Exception as err :
                    self.logger.error( err , exc_info=1 )
            out = 'DISCOVER %s SUCCESS %s' % ( HID , hosts  )
        except Exception as err :
            out = 'DISCOVER - FAILURE %s' % str( err )
            self.logger.error( err , exc_info=1 )
        if output:
            self.message.stdout( out )
        self.logger.debug( out )

    def do_MONITOR(self, args, output=True):
        """
        Monitors a host (i.e. MONITOR HID HOST -)
        @param args : arguments of operation
        @type args : string
        """
        OPERATION, HID, HOST, ARGS = args.split()
        try:
            info = ""
            for resname, resdict in list(self._resources.items()) :
                if self._config.resources[ resname ][ 'enable' ].lower() == 'false':
                    raise Exception( "Resource '%s' is not enable" % resname )
                if HOST in resdict['Resource'].host_list :
                    info = resdict['Resource'].host_properties( HOST )
                    resdict['Resource'].Communicator.close()
                    break
            assert info, "Host '%s' is not available" % HOST
            out = 'MONITOR %s SUCCESS %s' % (HID , info )
        except Exception as err :
            out = 'MONITOR %s FAILURE %s' % (HID , str(err) )
            self.logger.error( err , exc_info=1 )
        if output:
            self.message.stdout(out)
        self.logger.debug( out )

    def do_FINALIZE(self, args):
        """
        Finalizes the MAD (i.e. FINALIZE - - -)
        @param args : arguments of operation
        @type args : string
        """
        out = 'FINALIZE - SUCCESS -'
        self.message.stdout(out)
        self.logger.debug(out)
        sys.exit(0)

    methods = { 'INIT'    : do_INIT,
                'DISCOVER': do_DISCOVER,
                'MONITOR' : do_MONITOR,
                'FINALIZE': do_FINALIZE,
                }

    def processLine(self):
        """
        Choose the OPERATION through the command line
        """
        try:
            while True:
                input = sys.stdin.readline().split()
                self.logger.debug(' '.join(input))
                if len(input)>0:
                    OPERATION = input[0].upper()
                    if len(input) == 4 and OPERATION in self.methods:
                        self.methods[OPERATION](self, ' '.join(input))
                    else:
                        out = 'WRONG COMMAND'
                        self.message.stdout(out)
                        self.logger.debug(out)
        except Exception as err:
            self.logger.warning( str ( err ) , exc_info=1 )

import sys
import traceback
from argparse import ArgumentParser,SUPPRESS

def main():
    parser = ArgumentParser(
               description = 'Information manager MAD',
            )
    parser.add_argument('-v', '--version', action='version', version='0.1')
    #workaround for issue 
    #   https://github.com/SantanderMetGroup/DRM4G/issues/27
    parser.add_argument('null', nargs="*", type=str, help=SUPPRESS)
    parser.parse_args()
    try:
        GwImMad().processLine()
    except KeyboardInterrupt:
        return -1
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return 'Caught exception: %s: %s' % (e.__class__, str(e))

if __name__ == '__main__':
    sys.exit(main())
