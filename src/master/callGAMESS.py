'''
Created on Jul 15, 2015

This program calls the rungms command from the command line

@author: Alberto
'''
import subprocess
import os

class Call_rungms(object):
    
    def __init__(self,ver,proc):
        self.version=ver
        self.NCPUS=proc

    def name(self):
        for file in os.listdir(path='.'):
            if file.endswith(".inp"):
                self.nametot=str.split(file,".")
                self.name=self.nametot[0]
                return self.name
        
    def calling(self):
        proc= subprocess.Popen(["uname","-n"], stdout=subprocess.PIPE)
        self.wh=proc.stdout.read()
        if self.wh == b'cdm8-205\n':
            out=open(self.name+".log", mode='w')
            subprocess.call(["/home/student1/GAMESS/rungms",self.name+".inp",self.version,self.NCPUS], stdout=out)
        elif self.wh == b'lcmdlc2.cluster\n':
            out=open(self.name+".log", mode='w')
            subprocess.call(["/software/gamess/rungms",self.name+".inp",self.version,self.NCPUS], stdout=out)
            
        else:
            print("Not a valid hostname")
            
    def checking(self):
        self.error=""
        with open(self.name+".log", mode='r') as f:
            for line in f:
                if "SCF IS UNCONVERGED" in line:
                    print("Error: THE SCF is UNCONVERGED")
                    self.error="YES"
                    return self.error
                if "exited gracefully" in line:
                    print("GAMESS Job Completed")
                    self.complete="YES"
                    return self.complete
                    
        
        if self.error != "YES" and self.complete == "YES":
            print("Everything's OK!")     
                 
    def result(self):
        self.exactenergy=0
        if self.error != "YES":
            with open(self.name+".log", mode='r') as g:
                for line in g:
                    if "DFT EXCHANGE + CORRELATION"in line:
                        self.RXC=str.split(line)
                        self.EXC=float(self.RXC[6])
                        print('XC Energy: ', self.RXC[6])
                    elif "FINAL" in line:
                        self.RTOT=str.split(line)
                        self.ETOT=float(self.RTOT[4])
                        print('Total Energy: ',self.RTOT[4])
        
            self.exactenergy= self.ETOT-self.EXC
            print("Universal functional energy :", self.exactenergy)
       
        else:
            print("Error in SCF")
                    
                         
    def cleaning(self):
        subprocess.call(["rm",self.name+".log",self.name+".dat","PARAM.dat","PARAM_UNF.dat","alldata.test"])



t=Call_rungms('00','1')
t.name()
t.cleaning()
t.calling()
t.checking()
t.result()