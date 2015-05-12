#!/usr/bin/env python
"""
DRM4G is an open platform, which is based on GridWay Metascheduler, to define, 
submit, and manage computational jobs. For additional information, 
see http://meteo.unican.es/trac/wiki/DRM4G .

Usage: drm4g [ --version ] [ --help ]
             <command> [ options ] [ <args>... ]

Options:
    -h --help  Show help.
    --version  Show version.
    --dbg      Debug mode.
    
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
__version__  = '2.3.1'
__author__   = 'Carlos Blanco'
__revision__ = "$Id$"

from drm4g.utils.docopt import docopt

if __name__ == "__main__":
    args = docopt( __doc__, version = __version__ , options_first = True )
    argv = [ args[ '<command>' ] ] + args[ '<args>' ]
    if args['<command>'] in "start stop status restart clear conf id resource host job".split() :
        command = getattr( __import__( "drm4g.commands.%s" %  args['<command>'] ).commands, args['<command>'] )
        arg = docopt( command.__doc__ , argv = argv )
        command.run( arg )
    else:
        exit( "%r is not a drm4g command. See 'drm4g --help'." % args[ '<command>' ] )

