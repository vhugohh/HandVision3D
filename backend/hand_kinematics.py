import math,time
import numpy as np
CHAINS={'thumb':{'mcp':(1,2,3),'ip':(2,3,4)},'index':{'mcp':(0,5,6),'pip':(5,6,7),'dip':(6,7,8)},'middle':{'mcp':(0,9,10),'pip':(9,10,11),'dip':(10,11,12)},'ring':{'mcp':(0,13,14),'pip':(13,14,15),'dip':(14,15,16)},'pinky':{'mcp':(0,17,18),'pip':(17,18,19),'dip':(18,19,20)}}
def unit(v):
 v=np.asarray(v,float); n=np.linalg.norm(v); return v/n if n>1e-9 else np.zeros_like(v)
def angle(a,b,c):
 u=unit(a-b);v=unit(c-b);return math.degrees(math.acos(float(np.clip(np.dot(u,v),-1,1))))
def quat(m):
 tr=np.trace(m)
 if tr>0:
  s=math.sqrt(tr+1)*2;q=[(m[2,1]-m[1,2])/s,(m[0,2]-m[2,0])/s,(m[1,0]-m[0,1])/s,.25*s]
 elif m[0,0]>m[1,1] and m[0,0]>m[2,2]:
  s=math.sqrt(1+m[0,0]-m[1,1]-m[2,2])*2;q=[.25*s,(m[0,1]+m[1,0])/s,(m[0,2]+m[2,0])/s,(m[2,1]-m[1,2])/s]
 elif m[1,1]>m[2,2]:
  s=math.sqrt(1+m[1,1]-m[0,0]-m[2,2])*2;q=[(m[0,1]+m[1,0])/s,.25*s,(m[1,2]+m[2,1])/s,(m[0,2]-m[2,0])/s]
 else:
  s=math.sqrt(1+m[2,2]-m[0,0]-m[1,1])*2;q=[(m[0,2]+m[2,0])/s,(m[1,2]+m[2,1])/s,.25*s,(m[1,0]-m[0,1])/s]
 q=np.array(q);return (q/max(np.linalg.norm(q),1e-9)).tolist()
def calculate_pose(landmarks,label='Unknown',confidence=0):
 p=np.array([[x.x,x.y,x.z] for x in landmarks],float); fingers={}
 for name,joints in CHAINS.items():
  vals={k:round(float(np.clip(180-angle(p[a],p[b],p[c]),0,180)),1) for k,(a,b,c) in joints.items()}
  curl=round(float(np.mean(list(vals.values()))),1);fingers[name]={'joints':vals,'curl':curl,'extended':curl<38}
 width=max(np.linalg.norm(p[5]-p[17]),1e-5); pinch=float(np.linalg.norm(p[4]-p[8])/width)
 ext=sum(fingers[n]['extended'] for n in ('index','middle','ring','pinky')); thumb=fingers['thumb']['extended']
 gesture='pinch' if pinch<.42 else 'fist' if ext==0 and not thumb else 'open_palm' if ext>=4 and thumb else 'point' if fingers['index']['extended'] and ext<=2 else 'other'
 x=unit(p[5]-p[17]);y=unit(p[9]-p[0]);z=unit(np.cross(x,y));y=unit(np.cross(z,x));m=np.column_stack((x,y,z))
 palm=(p[0]+p[5]+p[9]+p[13]+p[17])/5
 euler={'pitch':math.degrees(math.atan2(-m[2,1],math.hypot(m[0,1],m[1,1]))),'yaw':math.degrees(math.atan2(m[1,0],m[0,0])),'roll':math.degrees(math.atan2(m[2,1],m[2,2]))}
 return {'handedness':label,'confidence':round(float(confidence),3),'position':{'wrist':p[0].tolist(),'palm':palm.tolist()},'orientation':{'quaternion':quat(m),'euler':euler},'fingers':fingers,'pinch_ratio':round(pinch,3),'gesture':gesture,'timestamp':time.time()}
class PoseSmoother:
 def __init__(self,alpha=.4):self.alpha=alpha;self.cache={}
 def apply(self,key,pose):
  old=self.cache.get(key);a=self.alpha
  if old is None:self.cache[key]=pose;return pose
  out=dict(pose);out['position']=dict(pose['position']);out['position']['palm']=(a*np.array(pose['position']['palm'])+(1-a)*np.array(old['position']['palm'])).tolist()
  out['fingers']={}
  for n,f in pose['fingers'].items():
   prev=old['fingers'][n];j={k:round(a*v+(1-a)*prev['joints'][k],1) for k,v in f['joints'].items()};c=round(float(np.mean(list(j.values()))),1);out['fingers'][n]={**f,'joints':j,'curl':c,'extended':c<38}
  q0=np.array(old['orientation']['quaternion']);q1=np.array(pose['orientation']['quaternion']);q1=-q1 if np.dot(q0,q1)<0 else q1;q=(a*q1+(1-a)*q0);q/=np.linalg.norm(q);out['orientation']=dict(pose['orientation']);out['orientation']['quaternion']=q.tolist();self.cache[key]=out;return out
