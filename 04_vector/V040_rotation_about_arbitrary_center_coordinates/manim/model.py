"""V040's independent, renderer-free rotation model; angles are in degrees."""
from dataclasses import dataclass
from math import cos, sin, radians, hypot


@dataclass(frozen=True)
class Rotation:
    center: tuple[float, float] = (1.0, 1.0)
    point: tuple[float, float] = (4.0, 2.0)

    @property
    def relative(self):
        return tuple(p-b for p,b in zip(self.point, self.center))

    @property
    def radius(self):
        return hypot(*self.relative)

    def components(self, degrees):
        u,v = self.relative
        c,s = cos(radians(degrees)),sin(radians(degrees))
        return (u*c,u*s),(-v*s,v*c)

    def rotated_relative(self, degrees):
        h,k = self.components(degrees)
        return h[0]+k[0],h[1]+k[1]

    def image(self, degrees):
        s,t = self.rotated_relative(degrees)
        a,b = self.center
        return a+s,b+t

    def corner(self, degrees):
        h,_ = self.components(degrees)
        return self.center[0]+h[0],self.center[1]+h[1]


LESSON = Rotation()

# Same timeline drives the scene and the automated key-state audit.
# Stage changes are annotations; no translation of the actual center is shown.
MOTIONS = (
    (45,2.4,1.0,"逆时针旋转 45°"),
    (90,1.8,1.2,"逆时针旋转 90°"),
    (0,1.5,0.4,"回到原来的位置"),
    (-45,2.4,1.2,"顺时针旋转，角度取负"),
    (0,1.5,0.4,"回到原来的位置"),
)
