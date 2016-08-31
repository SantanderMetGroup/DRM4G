#
# Copyright 2016 Universidad de Cantabria
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
import platform
from os.path     import dirname, abspath, join, expanduser, exists

import socket
import re
import logging
import drm4g.communicators
import drm4g.commands
from drm4g.commands         import Agent
from drm4g.communicators    import ComException, logger
from drm4g                  import SFTP_CONNECTIONS, SSH_CONNECT_TIMEOUT, DRM4G_DIR
from drm4g.utils.url        import urlparse
from openssh_wrapper import SSHConnection

__version__  = '2.5.0-0b2'
__author__   = 'Carlos Blanco'
__revision__ = "$Id$"

class Communicator(drm4g.communicators.Communicator):
    """
    Create a SSH session to remote resources.
    """
    _lock       = __import__('threading').Lock()
    _sem        = __import__('threading').Semaphore(SFTP_CONNECTIONS)
    _trans      = None

    def __init__(self):
        super(Communicator,self).__init__()
        self.configfile=join(DRM4G_DIR, 'etc', 'openssh.conf')
        self.conn=None
        self.agent=Agent()
        self.agent.start()
        self.agent_socket=self.agent.update_agent_env()['SSH_AUTH_SOCK']
        if not os.path.exists('~/.ssh/drm4g'):
            subprocess.call('mkdir -p ~/.ssh/drm4g', shell=True)

    def connect(self):
        """
        To establish the connection to resource.
        """
        if self.conn==None:
            self.conn = SSHConnection(self.frontend, login=self.username, port=str(self.port), configfile=self.configfile, identity_file=self.private_key, ssh_agent_socket=self.agent_socket, timeout=SSH_CONNECT_TIMEOUT)

    def execCommand(self , command , input = None ):
        self.connect()
        logger.info("execCommand")
        ret = self.conn.run(command)
        '''
        self.connect()
        with self._lock :
            channel = self._trans.open_session()
        channel.settimeout( SSH_CONNECT_TIMEOUT )
        channel.exec_command( command )
        if input :
            for line in input.split( ):
                channel.makefile( 'wb' , -1 ).write( '%s\n' % line )
                channel.makefile( 'wb' , -1 ).flush( )
        stdout = ''.join( channel.makefile( 'rb' , -1 ).readlines( ) )
        stderr = ''.join( channel.makefile_stderr( 'rb' , -1).readlines( ) )
        if channel :
            channel.close( )
        '''
        return ret.stdout , ret.stderr

    def mkDirectory(self, url):
        self.connect()
        logger.info('mkDirectory')
        to_dir         = self._set_dir(urlparse(url).path)
        stdout, stderr = self.execCommand( "mkdir -p %s" % to_dir )
        if stderr :
            raise ComException( "Could not create %s directory: %s" % ( to_dir , stderr ) )

    def rmDirectory(self, url):
        self.connect()
        logger.info('rmDirectory')
        to_dir         = self._set_dir(urlparse(url).path)
        stdout, stderr = self.execCommand( "rm -rf %s" % to_dir )
        if stderr:
            raise ComException( "Could not remove %s directory: %s" % ( to_dir , stderr ) )

    def copy( self , source_url , destination_url , execution_mode = '' ) :
        self.connect()
        logger.warning('copy')
        with self._sem :
            if 'file://' in source_url :
                from_dir = urlparse( source_url ).path
                to_dir   = self._set_dir( urlparse( destination_url ).path )
                self.conn.scp( [from_dir] , target=to_dir )
                if execution_mode == 'X':
                    stdout, stderr = self.execCommand( "chmod +x %s" % to_dir )
                    if stderr :
                        raise ComException( "Could not change access permissions of %s file: %s" % ( to_dir , stderr ) )        
            else:
                from_dir = self._set_dir( urlparse( source_url ).path )
                to_dir   = urlparse(destination_url).path
                self.remote_scp( [from_dir] , target=to_dir )

    #internal
    def _set_dir(self, path):
        logger.warning('_set_dir')
        work_directory =  re.compile( r'^~' ).sub( self.work_directory , path )
        return  work_directory


    def remote_scp(self, files, target):
        scp_command = self.scp_command(files, target)
        pipe = subprocess.Popen(scp_command,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, env=self.get_env())
        
        signal.alarm(SSH_CONNECT_TIMEOUT)
        err = ''
        try:
            _, err = pipe.communicate()
        except IOError as exc:
            # pipe.terminate() # only in python 2.6 allowed
            os.kill(pipe.pid, signal.SIGTERM)
            signal.alarm(0)  # disable alarm
            #cleanup_tmp_dir()
            raise ComException("%s (under %s): %s" % (' '.join(scp_command), self.username, str(exc)))
        signal.alarm(0)  # disable alarm
        returncode = pipe.returncode
        if returncode != 0:  # ssh client error
            #cleanup_tmp_dir()
            raise ComException("%s (under %s): %s" % (' '.join(scp_command), self.username, err.strip()))

    def scp_command(self, files, target, debug=False):
        """
        Build the command string to transfer the files identified by filenames.
        Include target(s) if specified. Internal function
        """
        cmd = ['/usr/bin/scp', debug and '-vvvv' or '-q', '-r']

        if self.username:
            remotename = '%s@%s' % (self.username, self.frontend)
        else:
            remotename = self.frontend
        if self.configfile:
            cmd += ['-F', self.configfile]
        if self.private_key:
            cmd += ['-i', self.private_key]
        if self.port:
            cmd += ['-P', str(self.port)]

        if not isinstance(files, list):
            raise ValueError('"files" argument have to be iterable (list or tuple)')
        if len(files) < 1:
            raise ValueError('You should name at least one file to copy')

        for f in files:
            cmd.append('%s:%s' % (remotename, f))
        cmd.append(target)
        return cmd

    def get_env(self):
        """
        Retrieve environment variables and replace SSH_AUTH_SOCK
        if ssh_agent_socket was specified on object creation.
        """
        env = os.environ.copy()
        if self.agent_socket: #should i check that it's empty? "if not env['SSH_AUTH_SOCK'] and self.agent_socket:"
            env['SSH_AUTH_SOCK'] = self.agent_socket
        return env