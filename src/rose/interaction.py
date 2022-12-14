'''
Defines a general template for interactions and specific, supported
interactions.
'''
from typing import Callable
import numpy as np
import numpy.typing as npt

from .constants import HBARC

class Interaction:
    '''
    Template class.
    '''
    def __init__(self,
        coordinate_space_potential: Callable[[float, npt.ArrayLike], float], # V(r, theta)
        mu: float, # reduced mass (MeV)
        is_complex: bool = False
    ):
        self.v_r = coordinate_space_potential
        self.mu = mu / HBARC # Go ahead and convert to 1/fm
        self.is_complex = is_complex
    

    def evaluate(self, r, pars):
        '''
        V(r, pars) where r is relative separation in fm
        The units returned here must match the units of energy, MeV.
        '''
        return self.v_r(r, pars)
    

    def tilde(self,
        s: float,
        alpha: npt.ArrayLike,
        energy: float
    ):
        '''
        tilde{U}(s, alpha, E)
        s = pr/hbar
        alpha are the parameters we are varying
        E = E_{c.m.}, [E] = MeV = [v_r]
        '''
        p = np.sqrt(2*self.mu*energy/HBARC) # 1/fm
        return  1.0/energy * self.v_r(s/p, alpha)


NUCLEON_MASS = 939.565 # neutron mass (MeV)
MU_NN = NUCLEON_MASS / 2 # reduced mass of the NN system (MeV)

def mn_potential(r, args):
    '''
    Minnesota potential
    '''
    v_0r, v_0s = args
    return v_0r * np.exp(-1.487*r**2) + v_0s*np.exp(-0.465*r**2)

# Stored instances of the Minnesota interaction for testing.
MN_Potential = Interaction(
    mn_potential,
    MU_NN
)

def complex_mn_potential(r, args):
    vr, vi = args
    return mn_potential(r, [vr, 1j*vi])


Optical_Potential = Interaction(
    complex_mn_potential,
    MU_NN,
    True
)