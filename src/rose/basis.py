from typing import Callable

import numpy as np 
import numpy.typing as npt

from .interaction import Interaction
from .schroedinger import SchroedingerEquation
from .free_solutions import phi_free

class Basis:
    def __init__(self,
        interaction: Interaction,
        theta_train: npt.ArrayLike, # training space
        s_mesh: npt.ArrayLike, # s = kr; discrete mesh where phi(s) is calculated
        n_basis: int, # number of basis vectors
        energy: float, # MeV, c.m.
        l: int # orbital angular momentum
    ):
        self.interaction = interaction
        self.theta_train = np.copy(theta_train)
        self.s_mesh = np.copy(s_mesh)
        self.n_basis = n_basis
        self.energy = energy
        self.l = l
    

    def phi_hat(self, coefficients):
        '''
        Every basis should know how to reconstruct hat{phi} from a set of
        coefficients. However, this is going to be different for each basis, so
        we will leave it up to the subclasses to implement this.
        '''
        raise NotImplementedError
    

class RelativeBasis(Basis):
    def __init__(self,
        interaction: Interaction,
        theta_train: npt.ArrayLike, # training space
        s_mesh: npt.ArrayLike, # s = kr; discrete mesh where phi(s) is calculated
        n_basis: int, # number of basis vectors
        energy: float, # MeV, c.m.
        l: int, # orbital angular momentum
        use_svd: bool # use principal components?
    ):
        super().__init__(interaction, theta_train, s_mesh, n_basis, energy, l)

        self.phi_0 = phi_free(self.s_mesh, l)

        schrodeq = SchroedingerEquation(self.interaction)
        if self.interaction.is_complex:
            d = dict(phi_0=0+0j, phi_prime_0=1+0j)
            self.all_vectors = np.array([
                schrodeq.phi(energy, theta, self.s_mesh, l, solve_se_dict=d) - self.phi_0 for theta in theta_train
            ]).T
        else:
            self.all_vectors = np.array([
                schrodeq.phi(energy, theta, self.s_mesh, l) - self.phi_0 for theta in theta_train
            ]).T

        if use_svd:
            U, S, _ = np.linalg.svd(self.all_vectors, full_matrices=False)
            self.singular_values = np.copy(S)
            self.all_vectors = np.copy(U)
        
        self.vectors = np.copy(self.all_vectors[:, :self.n_basis])
    

    def phi_hat(self, coefficients):
        return self.phi_0 + np.sum(coefficients * self.vectors, axis=1)
