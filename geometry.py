import numpy as np

TOL = 1.0e-9

def point_in_ccircle(ptest, a, b, c):
    
    # Must be a counter-clockwise boundary.

    dxy2 = ptest[0]**2 + ptest[1]**2

    M = [[a[0]-ptest[0], a[1]-ptest[1], a[0]**2 + a[1]**2 - dxy2],\
         [b[0]-ptest[0], b[1]-ptest[1], b[0]**2 + b[1]**2 - dxy2], \
         [c[0]-ptest[0], c[1]-ptest[1], c[0]**2 + c[1]**2 - dxy2]]
    
    return np.linalg.det(M) > 0.0


def pointOnFeatureLeft(pxy, fxy1, fxy2):
    # All coords specified as 2D numpy arrays.
    # pxy coords of the point to be tested.
    # fxy1 coords of the feature point 1.
    # fxy2 coords of the feature point 2.
    
    return (np.cross(fxy2-fxy1, pxy-fxy1) > 0.0)

def lineCrossingParameter(pxy, bnorm, fxy1, fxy2):
    
    bperp = np.array([-bnorm[1], bnorm[0]])
    
    dfxy = fxy2 - fxy1
    disc = np.dot(dfxy, bperp)
    
    if abs(disc) < np.linalg.norm(dfxy) * 1.0e-9:
        return None
    
    rlam = np.dot((pxy-fxy1), bperp) / disc
    
    return rlam
    
def pointInFeatureShadow(pxy, fxy1, fxy2, txy):
    # All coords specified as 2D numpy arrays.
    # pxy coords of the point to be tested.
    # fxy1 coords of the feature point 1.
    # fxy2 coords of the feature point 2.
    # txy coords of the origin.
    
    if not pointOnFeatureLeft(txy, fxy1, fxy2): fxy1, fxy2 = fxy2, fxy1
    
    bnorm = pxy - txy 
    bnorm = bnorm / np.linalg.norm(bnorm)
    
    rlam = lineCrossingParameter(txy, bnorm, fxy1, fxy2)

    if not rlam: return False
    if (rlam< TOL) | (rlam >1.0 - TOL): return False
    
    pint = fxy1 + rlam*(fxy2-fxy1)
    return (np.dot(pxy-pint, pint-txy) >= 0.0)

def lineInRayPath(txy, bnorm, fxy1, fxy2):
    # Determine if a ray path defined by point txy and the 
    # unit direction bnorm crosses the line segment [fxy1, fxy2]
    
    rlam = lineCrossingParameter(txy, bnorm, fxy1, fxy2)

    if not rlam: return False
    if (rlam<TOL) | (rlam >1.0-TOL): return False
    
    pint = fxy1 + rlam*(fxy2-fxy1)  # The intersection point.
    
    return np.dot(bnorm, pint-txy) >= TOL

def lineInFeatureShadow(pxy1, pxy2, fxy1, fxy2, txy):
    # Returns True if all or part of a line is obscured from
    # a given point by a feature line segment.
    
    # All coords specified as 2D numpy arrays.
    # pxy1 coords of the point 1 of the line to be tested.
    # pxy2 coords of the point 2 of the line to be tested.
    # fxy1 coords of the feature point 1.
    # fxy2 coords of the feature point 2.
    # txy coords of the origin.
    
    if pointInFeatureShadow(pxy1, fxy1, fxy2, txy): return True
    if pointInFeatureShadow(pxy2, fxy1, fxy2, txy): return True
    
    bnorm1 = fxy1 - txy
    bnorm1 = bnorm1 / np.linalg.norm(bnorm1)   
    if lineInRayPath(fxy1, bnorm1, pxy1, pxy2): return True
    
    bnorm2 = fxy2 - txy
    bnorm2 = bnorm2 / np.linalg.norm(bnorm2)
    if lineInRayPath(fxy2, bnorm2, pxy1, pxy2): return True
    
    return False

def elementInFeatureShadow(pxy1, pxy2, pxy3, fxy1, fxy2, txy):
    if pointInFeatureShadow(pxy1, fxy1, fxy2, txy): return True
    if pointInFeatureShadow(pxy2, fxy1, fxy2, txy): return True
    if pointInFeatureShadow(pxy3, fxy1, fxy2, txy): return True
    
    bnorm1 = fxy1 - txy
    bnorm1 = bnorm1 / np.linalg.norm(bnorm1)
    if lineInRayPath(fxy1, bnorm1, pxy1, pxy2): return True
    if lineInRayPath(fxy1, bnorm1, pxy1, pxy3): return True    
    if lineInRayPath(fxy1, bnorm1, pxy2, pxy3): return True
    
    bnorm2 = fxy2 - txy
    bnorm2 = bnorm2 / np.linalg.norm(bnorm2)
    if lineInRayPath(fxy2, bnorm2, pxy1, pxy2): return True
    if lineInRayPath(fxy2, bnorm2, pxy1, pxy3): return True    
    if lineInRayPath(fxy2, bnorm2, pxy2, pxy3): return True
    
    return False
    