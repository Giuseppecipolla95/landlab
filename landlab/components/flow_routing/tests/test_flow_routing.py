# -*- coding: utf-8 -*-
"""
test_flow_routing:

Created on Thurs Nov 12, 2015

@author: dejh

This just tests the functionality of the router in toto - no attempt is made
to test the submodules.
Sinks are tested as part of the lake_mapper.
"""

import landlab
from landlab import RasterModelGrid, FieldError
from landlab.components.flow_routing.route_flow_dn import FlowRouter
from numpy import sin, pi
import numpy as np  # for use of np.round
from numpy.testing import assert_array_equal, assert_array_almost_equal
from landlab import BAD_INDEX_VALUE as XX
from nose.tools import (with_setup, assert_true, assert_false, assert_raises,
                        assert_almost_equal, assert_equal)
try:
    from nose.tools import (assert_is, assert_set_equal, assert_dict_equal)
except ImportError:
    from landlab.testing.tools import (assert_is, assert_set_equal,
                                       assert_dict_equal)


def setup_dans_grid1():
    """
    Create a 5x5 test grid.
    This is a sheet flow test.
    """
    global fr, mg, infile
    global z, Q_in, A_target, frcvr_target, upids_target, Q_target, \
        steepest_target, links2rcvr_target

    mg = RasterModelGrid((5, 5), spacing=(10., 10.))

    infile = '../landlab/components/flow_routing/tests/test_fr_input.txt'

    z = mg.node_x.copy()

    Q_in = np.full(25, 2.)

    A_target = np.array([1.,  1.,  1.,  1.,  1.,
                         4.,  3.,  2.,  1.,  1.,
                         4.,  3.,  2.,  1.,  1.,
                         4.,  3.,  2.,  1.,  1.,
                         1.,  1.,  1.,  1.,  1.])*100.

    frcvr_target = np.array([0,  1,  2,  3,  4,
                             5,  5,  6,  7,  9,
                            10, 10, 11, 12, 14,
                            15, 15, 16, 17, 19,
                            20, 21, 22, 23, 24])

    upids_target = np.array([0,  1,  2,  3,  4,
                             5,  6,  7,  8,  9,
                            10, 11, 12, 13, 14,
                            15, 16, 17, 18, 19,
                            20, 21, 22, 23, 24])

    links2rcvr_target = np.full(25, XX)
    links2rcvr_target[mg.core_nodes] = np.array([24, 25, 26,
                                                 28, 29, 30,
                                                 32, 33, 34])

    Q_target = A_target * 2.  # only once Q_in is used

    steepest_target = np.array([0.,  0.,  0.,  0.,  0.,
                                0.,  1.,  1.,  1.,  0.,
                                0.,  1.,  1.,  1.,  0.,
                                0.,  1.,  1.,  1.,  0.,
                                0.,  0.,  0.,  0.,  0.])

    mg.add_field('node', 'topographic__elevation', z, units='-')


def setup_dans_grid2():
    """
    Create a 5x5 test grid.
    This tests more complex routing, with diffs between D4 & D8.
    """
    global fr, mg, infile
    global z, A_target_D8, A_target_D4, frcvr_target_D8, frcvr_target_D4, \
        upids_target_D8, upids_target_D4, steepest_target_D8, \
        steepest_target_D4, links2rcvr_target_D8, links2rcvr_target_D4

    mg = RasterModelGrid((5, 5), spacing=(10., 10.))

    infile = '../landlab/components/flow_routing/tests/test_fr_input.txt'

    z = np.array([7.,  7.,  7.,  7.,  7.,
                  7.,  5., 3.2,  6.,  7.,
                  7.,  2.,  3.,  5.,  7.,
                  7.,  1.,  2.,  4.,  7.,
                  7.,  0.,  7.,  7.,  7.])

    A_target_D8 = np.array([100.,   100.,   100.,   100.,   100.,
                            100.,   100.,   200.,   100.,   100.,
                            100.,   400.,   100.,   100.,   100.,
                            100.,   600.,   300.,   100.,   100.,
                            100.,  1000.,   100.,   100.,   100.])

    A_target_D4 = np.array([100.,   100.,   100.,   100.,   100.,
                            100.,   100.,   200.,   100.,   100.,
                            100.,   200.,   400.,   100.,   100.,
                            100.,   900.,   600.,   100.,   100.,
                            100.,  1000.,   100.,   100.,   100.])

    frcvr_target_D8 = np.array([0, 1, 2, 3, 4, 5, 11, 11, 7, 9, 10, 16, 16, 17,
                                14, 15, 21, 21, 17, 19, 20, 21, 22, 23, 24])

    frcvr_target_D4 = np.array([0, 1, 2, 3, 4, 5, 11, 12, 7, 9, 10, 16, 17, 12,
                                14, 15, 21, 16, 17, 19, 20, 21, 22, 23, 24])

    upids_target_D8 = np.array([0, 1, 2, 3, 4, 5, 9, 10, 14, 15, 19, 20, 21,
                                16, 11, 6, 7, 8, 12, 17, 13, 18, 22, 23, 24])

    upids_target_D4 = np.array([0, 1, 2, 3, 4, 5, 9, 10, 14, 15, 19, 20, 21,
                                16, 11, 6, 17, 12, 7, 8, 13, 18, 22, 23, 24])

    links2rcvr_target_D8 = np.full(25, XX)
    links2rcvr_target_D8[mg.core_nodes] = np.array([6, 51, 26,
                                                   11, 59, 61,
                                                   16, 67, 34])

    links2rcvr_target_D4 = np.full(25, XX)
    links2rcvr_target_D4[mg.core_nodes] = np.array([6,  7, 26,
                                                   11, 12, 30,
                                                   16, 33, 34])

    steepest_target_D8 = np.array([0., 0., 0., 0., 0.,
                                   0., 0.3, 0.08485281, 0.28, 0.,
                                   0., 0.1, 0.14142136, 0.21213203, 0.,
                                   0., 0.1, 0.14142136, 0.2,  0.,
                                   0., 0., 0., 0.,  0.])

    steepest_target_D4 = np.array([0., 0., 0., 0., 0.,
                                   0., 0.3, 0.02, 0.28, 0.,
                                   0., 0.1, 0.1, 0.2, 0.,
                                   0., 0.1, 0.1, 0.2, 0.,
                                   0., 0., 0., 0., 0.])

    mg.add_field('node', 'topographic__elevation', z, units='-')


@with_setup(setup_dans_grid1)
def test_check_fields():
    """
    Check to make sure the right fields have been created.
    """
    fr = FlowRouter(mg)
    assert_array_equal(z, mg.at_node['topographic__elevation'])
    assert_array_equal(np.zeros(25), mg.at_node['drainage_area'])
    assert_array_equal(np.ones(25), mg.at_node['water__volume_flux_in'])

    fr = FlowRouter(mg, infile)
    assert_array_equal(np.full(25, 2.), mg.at_node['water__volume_flux_in'])


@with_setup(setup_dans_grid1)
def test_check_field_input():
    """
    Check we can successfully pass water__volume_flux_in
    """
    mg.add_field('node', 'water__volume_flux_in',
                 np.full(25, 3.), units='m**3/s')
    fr = FlowRouter(mg)
    assert_array_equal(np.full(25, 3.), mg.at_node['water__volume_flux_in'])
    fr = FlowRouter(mg, infile)
    assert_array_equal(np.full(25, 2.), mg.at_node['water__volume_flux_in'])


@with_setup(setup_dans_grid1)
def test_accumulate_D8():
    """
    Test accumulation works for D8 in a simple scenario
    """
    fr = FlowRouter(mg)
    fr.route_flow()
    assert_array_equal(A_target, mg.at_node['drainage_area'])
    assert_array_equal(frcvr_target, mg.at_node['flow_receiver'])
    assert_array_equal(upids_target, mg.at_node['upstream_ID_order'])
    assert_array_equal(links2rcvr_target, mg.at_node['links_to_flow_receiver'])
    assert_array_equal(A_target, mg.at_node['water__volume_flux'])
    assert_array_equal(steepest_target,
                       mg.at_node['topographic__steepest_slope'])


@with_setup(setup_dans_grid1)
def test_variable_Qin():
    """
    Tests a variable Qin field.
    """
    Qin_local = np.zeros(25, dtype=float)
    Qin_local[13] = 2.
    mg.add_field('node', 'water__volume_flux_in',
                 Qin_local, units='m**3/s')
    fr = FlowRouter(mg)
    fr.route_flow()
    Qout_local = np.zeros_like(Qin_local)
    Qout_local[10:14] = 200.
    assert_array_equal(Qout_local, mg.at_node['water__volume_flux'])
    assert_array_equal(A_target, mg.at_node['drainage_area'])
    # note that A DOES NOT CHANGE when messing with Q_in


@with_setup(setup_dans_grid2)
def test_irreg_topo():
    """
    Tests D8 routing on a toy irregular topo.
    """
    fr = FlowRouter(mg)
    fr.route_flow(method='D8')
    assert_array_equal(A_target_D8, mg.at_node['drainage_area'])
    assert_array_equal(frcvr_target_D8, mg.at_node['flow_receiver'])
    assert_array_equal(upids_target_D8, mg.at_node['upstream_ID_order'])
    assert_array_equal(links2rcvr_target_D8,
                       mg.at_node['links_to_flow_receiver'])
    assert_array_almost_equal(steepest_target_D8,
                              mg.at_node['topographic__steepest_slope'])


@with_setup(setup_dans_grid2)
def test_irreg_topo():
    """
    Tests D4 routing on a toy irregular topo.
    """
    fr = FlowRouter(mg)
    fr.route_flow(method='D4')
    assert_array_equal(A_target_D4, mg.at_node['drainage_area'])
    assert_array_equal(frcvr_target_D4, mg.at_node['flow_receiver'])
    assert_array_equal(upids_target_D4, mg.at_node['upstream_ID_order'])
    assert_array_equal(links2rcvr_target_D4,
                       mg.at_node['links_to_flow_receiver'])
    assert_array_almost_equal(steepest_target_D4,
                              mg.at_node['topographic__steepest_slope'])
