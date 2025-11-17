#!/usr/bin/env python

import unittest
import numpy as np
import numpy.testing as nt

from dasst.ejection_models.comets import sublimation


class TestTEMP(unittest.TestCase):
    pass


class TestCrifo1997(unittest.TestCase):
    pass


class TestVaubaillon2005(unittest.TestCase):
    def setUp(self):
        self.params = dict(
            q=0.988,
            min_size=1e-4,
            max_size=1e-1,
            size_index=3,
            active_fraction=0.24,
            nucleus_radius=1.8e3,
            nucleus_geometric_albedo=0.04,
            afp_0=78.9e-2,
            observed_albedo=0.24,
            gamma=4 / 3,
            m_kg=18 * 1.66053906660e-27,
            dust_density=2e3,
            alpha_coef=1.2,
            index_of_variation=2.025,
            T_gas=175,
            time_of_outgassing=3.6e7,
            cos_za=1,
            max_au=3,
        )

    def test_total_mass_production(self):
        a_star0 = sublimation.critical_radius_crifo_1997(
            self.params["active_fraction"],
            self.params["q"],
            self.params["T_gas"],
            self.params["nucleus_radius"],
            self.params["cos_za"],
            self.params["nucleus_geometric_albedo"],
            self.params["gamma"],
            self.params["m_kg"],
            self.params["dust_density"],
        )
        Q_g = sublimation.total_number_production_vaubaillon_2005(
            self.params["T_gas"],
            self.params["size_index"],
            self.params["min_size"],
            self.params["max_size"],
            a_star0,
            self.params["alpha_coef"],
            self.params["gamma"],
            self.params["m_kg"],
            self.params["afp_0"],
            self.params["observed_albedo"],
            self.params["q"],
            self.params["q"],
            self.params["index_of_variation"],
        )
        self.assertAlmostEqual(Q_mt)

    def test_total_mass_production(self):
        a_star0 = sublimation.critical_radius_crifo_1997(
            self.params["active_fraction"],
            self.params["q"],
            self.params["T_gas"],
            self.params["nucleus_radius"],
            self.params["cos_za"],
            self.params["nucleus_geometric_albedo"],
            self.params["gamma"],
            self.params["m_kg"],
            self.params["dust_density"],
        )
        Q_m = sublimation.total_mass_production_vaubaillon_2005(
            self.params["T_gas"],
            self.params["size_index"],
            self.params["dust_density"],
            self.params["min_size"],
            self.params["max_size"],
            a_star0,
            self.params["alpha_coef"],
            self.params["gamma"],
            self.params["m_kg"],
            self.params["afp_0"],
            self.params["observed_albedo"],
            self.params["q"],
            self.params["q"],
            self.params["index_of_variation"],
        )
        self.assertAlmostEqual(Q_mt)

    def test_total_mass_loss(self):
        a_star0 = sublimation.critical_radius_crifo_1997(
            self.params["active_fraction"],
            self.params["q"],
            self.params["T_gas"],
            self.params["nucleus_radius"],
            self.params["cos_za"],
            self.params["nucleus_geometric_albedo"],
            self.params["gamma"],
            self.params["m_kg"],
            self.params["dust_density"],
        )
        M_loss_tot = sublimation.total_mass_loss_vaubaillon_2005(
            self.params["time_of_outgassing"],
            self.params["T_gas"],
            self.params["size_index"],
            self.params["dust_density"],
            self.params["min_size"],
            self.params["max_size"],
            a_star0,
            self.params["alpha_coef"],
            self.params["gamma"],
            self.params["m_kg"],
            self.params["afp_0"],
            self.params["observed_albedo"],
            self.params["q"],
            self.params["index_of_variation"],
            self.params["max_au"],
        )
        self.assertAlmostEqual()

