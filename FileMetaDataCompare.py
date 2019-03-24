
import grp
import pwd
import os ,sys
import pickle 
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--scanPath')
parser.add_argument('--storePath', default='/var/tmp',required=False)
parser.add_argument('--operation')
args = parser.parse_args()
scanPath = args.scanPath
storePath = args.storePath
operation = args.operation



def findOwnerPermission(filename):    
  stat_info = os.stat(filename)
  uid = stat_info.st_uid
  gid = stat_info.st_gid
  #print uid, gid
  oct_perm = oct(stat_info.st_mode)
  #print(oct_perm)
  user = pwd.getpwuid(uid)[0]
  group = grp.getgrgid(gid)[0]
  return oct_perm,user,group



def fileStateObject(scanPath,storePath,storedFileStat):
  for root, directories, filenames in os.walk(scanPath):
    print root
    for directory in directories:
      print os.path.join(root, directory) 
    for filename in filenames: 
      print os.path.join(root,filename)
      storedFileStat[filename]=findOwnerPermission(os.path.join(root,filename))
  return storedFileStat
            
def storeStateToSystem(scanPath,storePath,storedFileStat):      
  storedfile='filePermission'+scanPath.replace("/","-")+".stat"
  print(storedFileStat)
  f = open((os.path.join(storePath,storedfile)),"wb")
  pickle.dump(storedFileStat,f)
  f.close()

def fetchStateFromSystem(scanPath,storePath,savedFileStat):
  storedfile='filePermission'+scanPath.replace("/","-")+".stat"
  try:
    fl = open((os.path.join(storePath,storedfile)),'rb')
    savedFileStat = pickle.load(fl)
  except :
    print 'Could not Load File '+storedfile
    sys.exit(0)
  return savedFileStat

def compare(savedFileStat,currentFileStat):
  isAllWell=True
  for key in savedFileStat:
    if ((key in currentFileStat) and (savedFileStat[key]==currentFileStat[key])):
    #print( "Permissin not changed for "+key+" Expected= "+str(savedFileStat[key])+" Actual="+str(currentFileStat[key]))
      pass
    else:
      actual=currentFileStat[key] if key in currentFileStat else 'Not Found'
      print( "Permissin changed for "+key+" Expected= "+str(savedFileStat[key])+" Actual="+str(actual))
      isAllWell=False
  if isAllWell :
    print "ALL IS WELL..."

if __name__ == "__main__":
  currentFileStat={}
  if operation == "save":
    currentFileStat=fileStateObject(scanPath,storePath,currentFileStat)
    storeStateToSystem(scanPath,storePath,currentFileStat)
  elif operation == "compare" :
    savedFileStat={}
    currentFileStat=fileStateObject(scanPath,storePath,currentFileStat)
    savedFileStat=fetchStateFromSystem(scanPath,storePath,savedFileStat)
    compare(savedFileStat,currentFileStat)
#python test.py --scanPath '/var/log' --operation save
#python test.py --scanPath '/var/log' --storePath '/var/tmp' --operation compare
    
    
  
