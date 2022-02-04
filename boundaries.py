import math
import numpy as np

def spiral_example():
    thvals = np.linspace(0.0, 2.5*math.pi, 50)
    
    r0 = 2
    twopi = 2.0 * math.pi
    th = 0.0
    
    sp1 = [(1.0+4.0*th / twopi)*r0 * np.array([math.cos(th), math.sin(th)]) for th in thvals]
    sp2 = [((1.0+4.0*th / twopi)*r0 - 1.75) * np.array([math.cos(th), math.sin(th)]) for th in thvals]
    
    sp1.extend(sp2[-1::-1])
    
    return sp1
    
    
def square_c():
    theta = np.linspace(0.0, 3*math.pi/2.0, 16)
    nodeList = [[4.0*math.cos(th), 4.0*math.sin(th)] for th in theta]
    nodeList.extend([[0, -4.0 + 0.5*ii] for ii in range(1, 5)])

    nodeList.append([-2,-2])
    nodeList.append([-2,2])
    nodeList.append([2,2])
    nodeList.append([2,0])
    nodeList.extend([[2+0.5*ii, 0.0] for ii in range(1, 4)])
    
    return nodeList
    
def square_oo():
    theta = np.linspace(0.0, 3*math.pi/2.0, 16)
    nodeList = [[4.0*math.cos(th), 4.0*math.sin(th)] for th in theta]
    nodeList.extend([[0, -4.0 + 0.5*ii] for ii in range(1, 5)])

    nodeList.append([-2,-2])
    nodeList.append([-2,2])
    nodeList.append([2,2])
    nodeList.append([2,0])
      
    theta_additional = [th+math.pi for th in theta]

    newnodes = [[4.0*math.cos(th)+6.0, 4.0*math.sin(th)] for th in theta_additional]
   
    nodeList.extend(newnodes[1:])
    
    nodeList.extend([[6, 4-0.5*ii] for ii in range(1, 5)])
    nodeList.append([8, 2])
    nodeList.append([8,-2])
    nodeList.append([4,-2])
    
    return nodeList
    
def square_3o():
    theta = np.linspace(0.0, 3*math.pi/2.0, 16)
    nodeList = [[4.0*math.cos(th), 4.0*math.sin(th)] for th in theta]
    
    nodeList.append([2,-4])
    nodeList.append([2,-8])
    nodeList.append([-2,-8])
    nodeList.append([-2,-6])
    nodeList.extend([[-2 - 0.5*ii, -6.0] for ii in range(1, 5)])
    
    theta_additional = [th+math.pi for th in theta]
    newnodes = [[4.0*math.cos(th), 4.0*math.sin(th) - 6.0] for th in theta_additional] 
    nodeList.extend(newnodes[1:])

    nodeList.append([-2,-2])
    nodeList.append([-2,2])
    nodeList.append([2,2])
    nodeList.append([2,0])
      
    theta_additional = [th+math.pi for th in theta]
    newnodes = [[4.0*math.cos(th)+6.0, 4.0*math.sin(th)] for th in theta_additional] 
    nodeList.extend(newnodes[1:])
    
    nodeList.extend([[6, 4-0.5*ii] for ii in range(1, 5)])
    nodeList.append([8, 2])
    nodeList.append([8,-2])
    nodeList.append([4,-2])
    
    return nodeList