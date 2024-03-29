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
DRM4G is an open platform, which is based on GridWay Metascheduler, to define,
submit, and manage computational jobs. For additional information,
see http://meteo.unican.es/trac/wiki/DRM4G .

Usage: drm4g [ --version ] [ --help ]
             <command> [ options ] [ <args>... ]

Options:
    -h --help     Show help.
    -v --version  Show version.
    -d --debug    Debug mode.

drm4g commands are:
   start       Start DRM4G daemon and ssh-agent
   stop        Stop DRM4G daemon and ssh-agent
   status      Check DRM4G daemon and ssh-agent
   restart     Restart DRM4G daemon
   clear       Start DRM4G daemon deleting all the jobs available on DRM4G
   conf        Configure DRM4G daemon, scheduler and logger parameters
   resource    Manage computing resources
   id          Manage reosurce identities
   host        Print information about the hosts
   job         Submit, get status and history and cancel jobs

See 'drm4g <command> --help' for more information on a specific command.
"""

from difflib import get_close_matches
import logging
import drm4g
from drm4g.commands.docopt import docopt

commands_list = [
    'start',
    'host',
    'id',
    'job',
    'resource',
    'restart',
    'status',
    'stop',
    'clear',
    'conf'
]

def get_similar_commands(name):
    """Command name auto-correct."""
    name = name.lower()
    close_commands = get_close_matches(name, commands_list)
    if close_commands:
        return close_commands[0]
    return None
class CommandError(Exception):
    """Raised when there is an error in command-line arguments"""

def main():
    args = docopt( __doc__, version = drm4g.__version__ , options_first = True )
    cmd_name = args['<command>']
    argv = [ cmd_name ] + args[ '<args>' ]
    if cmd_name in commands_list :
        command = getattr( __import__( "drm4g.commands.%s" %  cmd_name ).commands, cmd_name )
        arg = docopt( command.__doc__ , argv = argv )
        if arg[ '--debug' ] :
            command.console_logger.setLevel(logging.DEBUG)
        command.run( arg )
    else:
        guess = get_similar_commands(cmd_name)
        msg = "%r is not a drm4g command" % cmd_name
        if guess:
            msg = msg + " - maybe you meant '%s'" % guess
        else:
            msg = msg + " - see 'drm4g --help'"
        return msg