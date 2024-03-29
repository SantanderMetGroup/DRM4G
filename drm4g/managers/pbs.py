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

import re
import drm4g.managers
from string import Template

import logging
logger  = logging.getLogger(__name__)

# The programs needed by these utilities. If they are not in a location
# accessible by PATH, specify their location here.
PBSNODES = 'LANG=POSIX pbsnodes' #pbsnodes - pbs node manipulation
QSUB     = 'LANG=POSIX qsub'     #qsub - submit pbs job
QSTAT    = 'LANG=POSIX qstat'    #qstat - show status of pbs batch jobs
QDEL     = 'LANG=POSIX qdel'     #qdel - delete pbs batch job

class Resource (drm4g.managers.Resource):

    def additional_queue_properties(self, queue):
        out, err = self.Communicator.execCommand('%s -q %s' % (QSTAT, queue.Name))
        #output line --> Queue Memory CPU_Time Walltime Node Run Que Lm State
        try:
            queueName, _, cpuTime, wallTime, _, _, _, lm = out.splitlines()[5].split()[0:8]
        except:
            logger.warning("Error parsing qstat: %s " % out)
        else:
            reTime = re.compile(r'(\d+):(\d+):\d+')
            if cpuTime != '--':
                try:
                    hours, minutes   = reTime.search(cpuTime).groups()
                    queue.MaxCpuTime = str(int(hours) * 60 + int(minutes))
                except:
                    pass
            if wallTime != '--':
                try:
                    hours, minutes   = reTime.search(wallTime).groups()
                    queue.MaxTime    = str(int(hours) * 60 + int(minutes))
                except:
                    pass
            if lm != '--':
                try:
                    queue.MaxRunningJobs = lm
                except:
                    pass
        return queue

class Job (drm4g.managers.Job):

    #pbs job status <--> GridWay job status
    states_pbs = {'E': 'ACTIVE',    #Job is exiting after having run.
                  'H': 'SUSPENDED', #Job is held.
                  'Q': 'PENDING',   #Job is queued, eligable to run or routed.
                  'R': 'ACTIVE',    #Job is running.
                  'T': 'PENDING',   #Job is being moved to new location.
                  'W': 'PENDING',   #Job is waiting for its execution time to be reached.
                  'S': 'SUSPENDED', #Job is suspend.
                  'C': 'DONE',	    #Job finalize.
                }

    def jobSubmit(self, pathScript):
        out, err = self.Communicator.execCommand('%s %s' % (QSUB, pathScript))
        if err:
            raise drm4g.managers.JobException(' '.join(err.split('\n')))
        return out.strip() #job_id

    def jobStatus(self):
        out, err = self.Communicator.execCommand('%s %s' % (QSTAT, self.JobId))
        if 'Unknown Job Id' in err :
            return 'DONE'
        elif err:
            return 'UNKNOWN'
        else:
            state = out.split()[-2]
            return self.states_pbs.setdefault(state, 'UNKNOWN')

    def jobCancel(self):
        out, err = self.Communicator.execCommand('%s %s' % (QDEL, self.JobId))
        if err:
            raise drm4g.managers.JobException(' '.join(err.split('\n')))

    def jobTemplate(self, parameters):
        
        # Dynamic directives
        args  = '#!/bin/bash\n'
        args += '#PBS -N JID_%s\n' % (parameters['environment']['GW_JOB_ID'])
        args += '#PBS -v %s\n' % (','.join(['%s=%s' %(k, v) for k, v in list(parameters['environment'].items())]))
        args += '#PBS -o $stdout\n'
        args += '#PBS -e $stderr\n'

        # Conditional directives
        if 'project' in parameters :
            args += '#PBS -P $project\n'
        if parameters['queue'] != 'default':
            args += '#PBS -q $queue\n'
        if 'maxWallTime' in parameters :
            args += '#PBS -l walltime=$maxWallTime\n'
        if 'maxCpuTime' in parameters :
            args += '#PBS -l cput=$maxCpuTime\n'
        if 'maxMemory' in parameters :
            args += '#PBS -l mem=${maxMemory}MB\n'
        if 'ppn' in parameters and 'nodes' in parameters :
            args += '#PBS -l nodes=$nodes:ppn=$ppn\n'
        elif 'ppn' in parameters :
            node_count = int(parameters['count']) / int(parameters['ppn'])
            if node_count == 0:
                node_count = 1
            args += '#PBS -l nodes=%d:ppn=$ppn\n' % (node_count)
        else:
            args += '#PBS -l nodes=$count\n'

        # Wrapper content
        args += '$executable\n'
        return Template(args).safe_substitute(parameters)


