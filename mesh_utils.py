def orderEdgesPolyline(ielist):
    
    ielist2 = [ielist[0]]
    n1 = ielist[0][2]
    n2 = ielist[0][3]
    n2found = True
    
    while n2found:
        n2found = False
        for ix, q in enumerate(ielist):
            if q[2] == n2:
                ielist2.append(q)
                n2 = q[3]
                n2found = True
                break
                
    n1found = True
    ielist3 = []
                
    while n1found:
        n1found = False
        for ix, q in enumerate(ielist):
            if q[3] == n1:                       
                ielist3.append(q)
                n1 = q[2]
                n1found = True
                break
    ielist3 = ielist3[-1::-1] # Reverse the order of ielist3            
    ielist3.extend(ielist2)
    ielist2 = ielist3
    
    return ielist2
    
  

def orderEdgesLoop(ielist):
    n2 = ielist[0][3]
    n_orig = ielist[0][2]
    istart = 1
    
    ielist2 = [ielist[0]]
    
    while n2 != n_orig:
        for ix, q in enumerate(ielist):
            if q[2] == n2:
                ielist2.append(q)
                n2 = q[3]
                break
                
    return ielist2
    
    
def findSingleElementEdges(islist, iolist, edges):
    # Make a list of edges that are referenced by one element only.
    ielist = [] 
    
    for q in islist:
        if islist[q] == 1:
            n1, n2 = edges[q]['nodes']
            if not iolist[q]: n1, n2 = n2, n1
            ielist.append((q, iolist[q], n1, n2)) # edge + orientation + nodes in order
            
    return ielist