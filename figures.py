import numpy as np

WHITE = (1,1,1)
BLACK = (0,0,0)

OPAQUE = 0
REFLECTIVE = 1
TRANSPARENT = 2


class Intersect(object):
    def __init__(self, distance, point, normal, sceneObj):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.sceneObj = sceneObj

class Material(object):
    def __init__(self, diffuse = WHITE, spec = 1.0, ior = 1.0, matType = OPAQUE):
        self.diffuse = diffuse
        self.spec = spec
        self.ior = ior
        self.matType = matType


class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def ray_intersect(self, orig, dir):
        L = np.subtract(self.center, orig)
        tca = np.dot(L, dir)
        d = (np.linalg.norm(L) ** 2 - tca ** 2) ** 0.5

        if d > self.radius:
            return None

        thc = (self.radius ** 2 - d ** 2) ** 0.5

        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None
        
        # P = O + t0 * D
        P = np.add(orig, t0 * np.array(dir))
        normal = np.subtract(P, self.center)
        normal = normal / np.linalg.norm(normal)

        return Intersect(distance = t0,
                        point = P,
                        normal = normal,
                        sceneObj = self)

class Plane(object):
    def __init__(self, position, normal, material) -> None:
        self.position = position
        self.normal = normal / np.linalg.norm(normal)
        self.material = material
        
    def ray_intersect(self, orig, dir):
        denom = np.dot(dir, self.normal)
        
        if abs(denom) > 0.0001:
            num = np.dot(np.subtract(self.position, orig), self.normal)
            
            t = num / denom
            
            if t > 0:
                P = np.add(orig, t*np.array(dir))
                
                return Intersect(distance = t,
                        point = P,
                        normal = self.normal,
                        sceneObj = self)

        return None
    
class AABB(object):
    def __init__(self,position, size, material) -> None:
        self.position = position
        self.size = size
        self.material = material
        self.planes = []
        
        halfSizes = [0,0,0]
        
        halfSizes[0] = size[0]/2
        halfSizes[1] = size[1]/2
        halfSizes[2] = size[2]/2
        
        #sides
        self.planes.append( Plane(np.add(position, (halfSizes[0], 0,0)), (1,0,0), material))
        self.planes.append( Plane(np.add(position, (-halfSizes[0], 0,0)), (-1,0,0), material))
        
        #up and down
        self.planes.append( Plane(np.add(position, (0, halfSizes[1], 0)), (0,1,0), material))
        self.planes.append( Plane(np.add(position, (0, -halfSizes[1], 0)), (0,-1,0), material))
        
        #fron and back
        self.planes.append( Plane(np.add(position, (0,0,halfSizes[2])), (0,0,1), material))
        self.planes.append( Plane(np.add(position, (0,0,halfSizes[2])), (0,0,-1), material))
        
        
        self.boundsMin = [0,0,0]
        self.boundsMax = [0,0,0]
        
        epsilon = 0.001
        
        for i in range(3):
            self.boundsMin[i] = self.position[i] - (epsilon + halfSizes[i])
            self.boundsMax[i] = self.position[i] + (epsilon + halfSizes[i])
        
        
    def ray_intersect(self, orig, dir):
        intersect = None
        t = float('inf')
        
        for plane in self.planes:
            planeInter = plane.ray_intersect(orig, dir)
            if planeInter is not None:
                planePoint = planeInter.point
                
                if self.boundsMin[0] <= planePoint[0] <= self.boundsMax[0]:
                    if self.boundsMin[1] <= planePoint[1] <= self.boundsMax[1]:
                        if self.boundsMin[2] <= planePoint[2] <= self.boundsMax[2]:
                            if planeInter.distance < t:
                                t = planeInter.distance
                                intersect = planeInter
        
        if intersect is None:
            return None
                        
                        
        return Intersect(distance = t,
                        point = intersect.point,
                        normal = intersect.normal,
                        sceneObj = self)
                    
        