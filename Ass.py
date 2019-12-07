import simpy
#import random
import numpy.random as random
import matplotlib.pyplot as plt
''' ------------------------ '''
''' Parameters               '''
''' ------------------------ '''
'Max Simulation Time'
MAXSIMTIME = 4000 
' "True"  Print to terminal'
VERBOSE = False 
P11 = 0.2
P12 = 1-P11
LAMBDA = 6.0
MU1 = 11.0
MU2 = 14.0
LAMBDA1 = LAMBDA/P12
LAMBDA2 = LAMBDA
POPULATION = 50000000
SERVICE_DISCIPLINE = 'FIFO'
LOGGED = True
'Probability Job Queue has more than ProN job(s)'
ProN = 4.0 
'Number of Replications'
REPS = 10.0 
'Identify the knee'
kneeDeltaRate = 0.005 
INTER_SERVICE_TIME_1 = 1/MU1
INTER_SERVICE_TIME_2 = 1/MU2


''' ------------------------ '''
''' DES model                '''
''' ------------------------ '''
class Job:
    def __init__(self, name, arrtime, duration):
        self.name = name
        self.arrtime = arrtime
        self.duration = duration

    def __str__(self):
        return '%s at %d, length %d' %(self.name, self.arrtime, self.duration)

def SJF( job ):
    return job.duration

class point:
    def __init__(self,value,time):
        self.value=value
        self.time= time

''' A server
 - env: SimPy environment
 - strat: - FIFO: First In First Out
          - SJF : Shortest Job First
'''
class Server:
    def __init__(self, env,server, strat = 'FIFO',mu1 = 5.0, mu2 = 8.0):
        self.env = env
        self.server = server
        self.servicetime1=float(1/float(mu1))
        self.servicetime2=float(1/float(mu2))
        self.strat = strat
        self.Jobs = list(())
        self.JobsInSystem = 0.0
        self.serversleeping = None
        ''' statistics '''
        self.waitingTime = 0
        self.idleTime = 0
        self.jobsDone = 0
        self.ProbMoreThanNjobs = 0
        self.MeanJobInSystem = 0
        self.VarJobInSystem = 0
        self.systemJob = list(())
        self.queuelength = list(())
        self.queuetime = list (())
        
        ''' register a new server process '''
        env.process( self.serve() )

    def serve(self):
        while True:
            ''' do nothing, just change server to idle
              and then yield a wait event which takes infinite time
            '''
            if len( self.Jobs ) == 0 :
                self.serversleeping = env.process( self.waiting( self.env ))
                t1 = self.env.now
                yield self.serversleeping
                ''' accumulate the server idle time'''
                self.idleTime += self.env.now - t1
            else:
                ''' get the first job to be served'''
                if self.strat == 'SJF':
                    self.Jobs.sort( key = SJF )
                    j = self.Jobs.pop( 0 )
                else: # FIFO by default
                    j = self.Jobs.pop( 0 )
                'if (env.now % 10 == 0) :'
                self.systemJob.append(self.JobsInSystem)
                self.queuelength.append(len(self.Jobs))
                self.queuetime.append(env.now)
                '''if LOGGED:
                    qlog.write( '%.4f\t%d\t%d\n' 
                        % (self.env.now, 1 if len(self.Jobs)>0 else 0, len(self.Jobs)) )'''

                ''' sum up the waiting time'''
                self.waitingTime += self.env.now - j.arrtime
                ''' yield an event for the job finish'''
                yield self.env.timeout( j.duration )
                'self.server.Jobs.append(Job("Job",env.now,j.duration))'
                ''' sum up the jobs done '''
                if random.randint(0,11)<=(P11*10) :
                    '''duration1=random.exponential(self.servicetime1)'''
                    job_interservice = random.exponential( INTER_SERVICE_TIME_1 )
                    self.Jobs.append(Job(j.name, env.now, job_interservice))
                    'self.queuelength.append(len(self.Jobs))'
                    'self.queuetime.append(env.now)'
                else :
                    self.JobsInSystem -= 1
                    '''duration2=random.exponential(self.servicetime2)'''
                    job_interservice = random.exponential( INTER_SERVICE_TIME_2 )
                    self.server.Jobs.append(Job(j.name, env.now, job_interservice))
                    'self.server.queuelength.append(len(self.Jobs))'
                    'self.server.queuetime.append(env.now)'
                if not self.server.serversleeping.triggered:
                    self.server.serversleeping.interrupt('Wake up, please.')
                self.jobsDone += 1
    def MeanJobInSystemComputing(self, k):
        i = k
        JobxTime = 0
        while i < len(self.queuetime) - 1:
                JobxTime += self.systemJob[i] * (self.queuetime[i+1] - self.queuetime[i])
                i += 1
        self.MeanJobInSystem = JobxTime/(MAXSIMTIME - self.queuetime[k])  
    def VarOfJobInSystemComputing(self, k):
        i = k
        SquaredDeltaJobxTime = 0
        while i < len(self.queuetime) - 1:
                SquaredDeltaJobxTime += ((self.systemJob[i] - self.MeanJobInSystem)**2)  * (self.queuetime[i+1] - self.queuetime[i-1])
                i += 1
        self.VarJobInSystem = SquaredDeltaJobxTime/(MAXSIMTIME - self.queuetime[k])          
    def ProbMoreThanNjobsComputing(self, N, k):
        i = k
        totalTime = 0
        while i < len(self.queuetime) - 1:
            if self.systemJob[i] > N:
                totalTime += self.queuetime[i+1] - self.queuetime[i-1]
            i += 1
        self.ProbMoreThanNjobs = totalTime/(MAXSIMTIME - self.queuetime[k])  
    def waiting(self, env):
        try:
            if VERBOSE:
                print( 'Server 1 is idle at %.2f' % self.env.now )
            yield self.env.timeout( MAXSIMTIME )
        except simpy.Interrupt as i:
            if VERBOSE:
                 print('Server 1 waken up and works at %.2f' % self.env.now )

class Server2:
    def __init__(self, env, strat = 'SJF'):
        self.env = env
        self.strat = strat
        self.Jobs = list(())
        self.serversleeping = None
        ''' statistics '''
        self.waitingTime = 0
        self.idleTime = 0
        self.jobsDone = 0
        self.queuelength = list(())  
        self.queuetime = list (())        
        ''' register a new server process '''
        env.process( self.serve() )

    def serve(self):
        while True:
            ''' do nothing, just change server to idle
              and then yield a wait event which takes infinite time
            '''
            if len( self.Jobs ) == 0 :
                self.serversleeping = env.process( self.waiting( self.env ))
                t1 = self.env.now
                yield self.serversleeping
                ''' accumulate the server idle time'''
                self.idleTime += self.env.now - t1
            else:
                ''' get the first job to be served'''
                if self.strat == 'SJF':
                    self.Jobs.sort( key = SJF )
                    j = self.Jobs.pop( 0 )
                else: # FIFO by default
                    j = self.Jobs.pop( 0 )
                self.queuelength.append(len(self.Jobs))
                self.queuetime.append(env.now)
                '''if LOGGED:
                    qlog.write( '%.4f\t%d\t%d\n'
                        % (self.env.now, 1 if len(self.Jobs)>0 else 0, len(self.Jobs)) )'''

                ''' sum up the waiting time'''
                self.waitingTime += self.env.now - j.arrtime
                ''' yield an event for the job finish'''
                yield self.env.timeout( j.duration )
                ''' sum up the jobs done '''
                self.jobsDone += 1

    def waiting(self, env):
        try:
            if VERBOSE:
                print( 'Server 2 is idle at %.2f' % self.env.now )
            yield self.env.timeout( MAXSIMTIME )
        except simpy.Interrupt as i:
            if VERBOSE:
                 print('Server 2 waken up and works at %.2f' % self.env.now )

class JobGenerator:
    def __init__(self, env, server, nrjobs = 10000000, lam = LAMBDA, mu = MU1):
        self.server = server
        self.nrjobs = nrjobs
        self.interarrivaltime = 1/lam
        env.process( self.generatejobs(env) )

    def generatejobs(self, env):
        i = 1
        while True:
            '''yield an event for new job arrival'''
            job_interarrival = random.exponential( self.interarrivaltime )
            yield env.timeout( job_interarrival )
            ''' generate service time and add job to the list'''
            job_duration = random.exponential( INTER_SERVICE_TIME_1 )
            self.server.Jobs.append( Job('Job %s' %i, env.now, job_duration) )
            self.server.JobsInSystem += 1
            self.server.systemJob.append(self.server.JobsInSystem)
            self.server.queuelength.append(len(self.server.Jobs))
            self.server.queuetime.append(env.now)
            if VERBOSE:
                print( 'job %d: t = %.2f, l = %.2f, dt = %.2f' 
                    %( i, env.now, job_duration, job_interarrival ) )
            i += 1

            ''' if server is idle, wake it up'''
            if not self.server.serversleeping.triggered:
                self.server.serversleeping.interrupt( 'Wake up, please.' )

'''Transient Remove'''
EnvReps = list(())
QueueLenRepsList = list(())
QueueTimeRepsList = list(())
MyServer2 = list(())
MyServer = list(())
MyJobGeneration = list(())
MeanJlength  = list(())
MeanJtime    = list(())
MeanLlength  = list(())
MeanLtime    = list(())
RateMeanL     = list(())
RateMeanLtime = list(())
timeList = list(())
MeanOverall = 0.0
MeanLdel = 0.0
minRepsLen = 0.0
kneePos = 0
i = 0
while(i < 10):
    EnvReps.append(simpy.Environment())
    MyServer2.append(Server2( EnvReps[i], SERVICE_DISCIPLINE ))
    MyServer.append(Server( EnvReps[i],MyServer2[i], SERVICE_DISCIPLINE,MU1 ,MU2 ))
    MyJobGeneration.append(JobGenerator( EnvReps[i], MyServer[i], POPULATION, LAMBDA, MU1 ))
    env = EnvReps[i]
    env.run(until = MAXSIMTIME)
    QueueLenRepsList.append(MyServer[i].systemJob)
    QueueTimeRepsList.append(MyServer[i].queuetime)
    print('%d' %len(MyServer[i].queuetime))
    MeanOverallRun = 0
    if i == 0:
        minRepsLen = len(MyServer[0].queuetime)
        t = 0
        while (t < minRepsLen) :
            MeanJlength.append(MyServer[0].systemJob[t])
            MeanJtime.append(MyServer[0].queuetime[t])
            t += 1
    else:
        if (len(MyServer[i].queuetime) < minRepsLen) :
            minRepsLen = len(MyServer[i].queuetime)
        t = 0
        while (t < minRepsLen) :
            MeanJlength[t] += MyServer[i].systemJob[t]
            t += 1
    i += 1
'''-----------MEAN OVERALL------------'''
i = 0
while i < minRepsLen :
    MeanOverallRun += MeanJlength[i]
    MeanJlength[i] = MeanJlength[i]*0.1
    i += 1
'---------------------------------------'
MeanOverall = MeanOverallRun*1.0/(minRepsLen*REPS)    
'----------------------------------------'
print('%d' %minRepsLen)
if LOGGED:
    qlog = open( 'mm1-l%d-m%d.csv' % (LAMBDA,MU1), 'w' )
    qlog.write( '0\t0\t0\n' )
'---MEAN DELETE FIRST L OBSERVATION(S)---'
i = 0
while i < minRepsLen - 1 :
    '''if((RateMeanL[i]  - RateMeanL[i - 1])/(RateMeanLtime[i] - RateMeanLtime[i-1]) < kneeDeltaRate):
        kneePos = i
        break'''
    MeanOverallRun -= MeanJlength[i]*10.0
    MeanLlength.append(MeanOverallRun/(minRepsLen - i - 1))
    qlog.write('%f\t' %(MeanJlength[i]))
    RateMeanL.append((MeanLlength[i] - MeanOverall)/MeanOverall)
    timeList.append(i)
    qlog.write('%f\n' %(RateMeanL[i]))
    i += 1
print('%f' %kneePos)
plt.plot(timeList, RateMeanL)
plt.xlabel('Time')
plt.show

''' close log file '''
if LOGGED:
    qlog.close()
   



''' start SimPy environment '''
env = simpy.Environment()
MyServer2 = Server2( env, SERVICE_DISCIPLINE )
MyServer = Server( env,MyServer2, SERVICE_DISCIPLINE,MU1 ,MU2 )
MyJobGenerator = JobGenerator( env, MyServer, POPULATION, LAMBDA, MU1 )
env.run(MAXSIMTIME)
MyServer.MeanJobInSystemComputing( kneePos)
MyServer.VarOfJobInSystemComputing( kneePos)
MyServer.ProbMoreThanNjobsComputing( ProN, kneePos)
MeanJob = MyServer.MeanJobInSystem
VarJob = MyServer.VarJobInSystem


''' start simulation '''





''' print statistics '''
RHO1 = LAMBDA1/MU1
RHO2 = LAMBDA2/MU2
print( 'Arrivals               : %d' % (MyServer.jobsDone) )
print( 'Utilization            : %.2f/%.2f' 
    % (1.0-MyServer.idleTime/MAXSIMTIME, RHO1) )
print( 'Mean waiting time      : %.2f/%.2f' 
    % (MyServer.waitingTime/MyServer.jobsDone, RHO1**2/((1-RHO1)*LAMBDA1) ) )

print( 'Arrivals               : %d' % (MyServer2.jobsDone) )
print( 'Utilization            : %.2f/%.2f'
    % (1.0-MyServer2.idleTime/MAXSIMTIME, RHO2) )
print( 'Mean waiting time      : %.2f/%.2f'
    % (MyServer2.waitingTime/MyServer2.jobsDone, RHO2**2/((1-RHO2)*LAMBDA2) ) )

fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle('Jobs in queue')
ax1.step(MyServer.queuetime,MyServer.queuelength)
ax1.set(xlabel='', ylabel='Queue 1')
ax2.step(MyServer2.queuetime,MyServer2.queuelength)
ax2.set(xlabel='Time', ylabel='Queue 2')
plt.show()

