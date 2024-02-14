# -*- coding: utf-8 -*-
# 
# This is an example of a class encapsulating a frame model. 
# The class is used to solve the frame model and display the results.
#
# The model is a simple 2D frame with three beams. The beams are
# connected at the top and bottom nodes. The beams have different
# cross sections and material properties. The frame is loaded with
# a distributed load and a point load. The frame is fixed at the
# bottom nodes.
#
# The model is solved using the calfem finite element library.
# The results are displayed using the calfem matplotlib visualization
# library.
#

import numpy as np
import calfem.core as cfc
import calfem.utils as cfu
import calfem.vis_mpl as cfv

class FrameModel:
    def __init__(self):
        """Initializes the model with default values."""

        self.w = 6.0
        self.h = 4.0
        self.E = 200.0e9
        self.A1 = 2.0e-3
        self.A2 = 6.0e-3
        self.I1 = 1.6e-5
        self.I2 = 5.4e-5
        self.q1 = 0.0
        self.q2 = -10e3
        self.q3 = 0.0
        self.f1 = 2e3

        self.edof = np.array([
            [4, 5, 6, 1, 2, 3], 
            [7, 8, 9, 10, 11, 12], 
            [4, 5, 6, 7, 8, 9]
        ])

    def solve(self):
        """Solves the model."""

        ep1 = np.array([self.E, self.A1, self.I1])
        ep3 = np.array([self.E, self.A2, self.I2])
        self.ex1 = np.array([0, 0])
        self.ex2 = np.array([self.w, self.w])
        self.ex3 = np.array([0, self.w])
        self.ey1 = np.array([self.h, 0])
        self.ey2 = np.array([self.h, 0])
        self.ey3 = np.array([self.h, self.h])
        eq1 = np.array([0, self.q1])
        eq2 = np.array([0, self.q2])
        eq3 = np.array([0, self.q3])

        Ke1, fe1 = cfc.beam2e(self.ex1, self.ey1, ep1, eq1)
        Ke2, fe2 = cfc.beam2e(self.ex2, self.ey2, ep1, eq2)
        Ke3, fe3 = cfc.beam2e(self.ex3, self.ey3, ep3, eq3)

        # ----- Assemble Ke into K ---------------------------------------

        K = np.array(np.zeros((12, 12)))
        f = np.array(np.zeros((12, 1)))
        f[3] = self.f1

        K, f = cfc.assem(self.edof[0, :], K, Ke1, f, fe1)
        K, f = cfc.assem(self.edof[1, :], K, Ke2, f, fe2)
        K, f = cfc.assem(self.edof[2, :], K, Ke3, f, fe3)

        # ----- Solve the system of equations and compute reactions ------

        bc = np.array([1, 2, 3, 10, 11])
        self.a, self.r = cfc.solveq(K, f, bc)

        self.ed = cfc.extract_ed(self.edof, self.a)

        self.es1, self.edi1, self.ec1 = cfc.beam2s(self.ex1, self.ey1, ep1, self.ed[0, :], eq1, nep=21)
        self.es2, self.edi2, self.ec2 = cfc.beam2s(self.ex2, self.ey2, ep1, self.ed[1, :], eq2, nep=21)
        self.es3, self.edi3, self.ec3 = cfc.beam2s(self.ex3, self.ey3, ep3, self.ed[2, :], eq3, nep=21)

    def print_results(self):
        """Prints the results of the model."""

        cfu.disp_h2("es1")
        cfu.disp_array(self.es1, ["N", "Vy", "Mz"])
        cfu.disp_h2("edi1")
        cfu.disp_array(self.edi1, ["u1", "v1"])
        cfu.disp_h2("es2")
        cfu.disp_array(self.es2, ["N", "Vy", "Mz"])
        cfu.disp_h2("edi2")
        cfu.disp_array(self.edi2, ["u1", "v1"])
        cfu.disp_h2("es3")
        cfu.disp_array(self.es3, ["N", "Vy", "Mz"])
        cfu.disp_h2("edi3")
        cfu.disp_array(self.edi3, ["u1", "v1"])

    def draw_deformed(self):
        """Draws the deformed model."""

        plotpar = [2, 1, 0]
        sfac = cfv.scalfact2(self.ex3, self.ey3, self.edi3, 0.1)
        print("sfac=")
        print(sfac)

        cfv.figure(1)
        cfv.eldraw2(self.ex1, self.ey1, plotpar)
        cfv.eldraw2(self.ex2, self.ey2, plotpar)
        cfv.eldraw2(self.ex3, self.ey3, plotpar)

        plotpar = [1, 2, 1]
        cfv.dispbeam2(self.ex1, self.ey1, self.edi1, plotpar, sfac)
        cfv.dispbeam2(self.ex2, self.ey2, self.edi2, plotpar, sfac)
        cfv.dispbeam2(self.ex3, self.ey3, self.edi3, plotpar, sfac)
        cfv.axis([-1.5, 7.5, -0.5, 5.5])
        plotpar1 = 2
        cfv.scalgraph2(sfac, [1e-2, 0.5, 0], plotpar1)
        cfv.title("Displacements")

    def draw_normal_forces(self):
        """Draws the normal forces."""

        plotpar = [2, 1]
        sfac = cfv.scalfact2(self.ex1, self.ey1, self.es1[:, 0], 0.2)
        cfv.figure(2)
        cfv.secforce2(self.ex1, self.ey1, self.es1[:, 0], plotpar, sfac)
        cfv.secforce2(self.ex2, self.ey2, self.es2[:, 0], plotpar, sfac)
        cfv.secforce2(self.ex3, self.ey3, self.es3[:, 0], plotpar, sfac)
        cfv.axis([-1.5, 7.5, -0.5, 5.5])
        plotpar1 = 2
        cfv.scalgraph2(sfac, [3e4, 1.5, 0], plotpar1)
        cfv.title("Normal force")

    def draw_shear_forces(self):
        """Draws the shear forces."""

        plotpar = [2, 1]
        sfac = cfv.scalfact2(self.ex3, self.ey3, self.es3[:, 1], 0.2)
        cfv.figure(3)
        cfv.secforce2(self.ex1, self.ey1, self.es1[:, 1], plotpar, sfac)
        cfv.secforce2(self.ex2, self.ey2, self.es2[:, 1], plotpar, sfac)
        cfv.secforce2(self.ex3, self.ey3, self.es3[:, 1], plotpar, sfac)
        cfv.axis([-1.5, 7.5, -0.5, 5.5])
        plotpar1 = 2
        cfv.scalgraph2(sfac, [3e4, 0.5, 0], plotpar1)
        cfv.title("Shear force")   

    def draw_moments(self):
        """Draws the moments."""

        plotpar = [2, 1]
        sfac = cfv.scalfact2(self.ex3, self.ey3, self.es3[:, 2], 0.2)
        print("sfac=")
        print(sfac)

        cfv.figure(4)
        cfv.secforce2(self.ex1, self.ey1, self.es1[:, 2], plotpar, sfac)
        cfv.secforce2(self.ex2, self.ey2, self.es2[:, 2], plotpar, sfac)
        cfv.secforce2(self.ex3, self.ey3, self.es3[:, 2], plotpar, sfac)
        cfv.axis([-1.5, 7.5, -0.5, 5.5])
        plotpar1 = 2
        cfv.scalgraph2(sfac, [3e4, 0.5, 0], plotpar1)
        cfv.title("Moment")    

    def show_and_wait(self):
        """Shows the plots and waits for the user to close them."""
        cfv.show_and_wait() 

if __name__ == "__main__":

    model = FrameModel()

    model.w = 6.0
    model.h = 4.0
    model.E = 200.0e9
    model.q1 = 0.0
    model.q2 = 0.0
    model.q3 = -10e3
    model.f1 = 2e3

    model.solve()

    model.print_results()

    model.draw_deformed()
    model.draw_normal_forces()
    model.draw_shear_forces()
    model.draw_moments()
    model.show_and_wait()