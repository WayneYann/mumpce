.. mumpce documentation master file, created by
   sphinx-quickstart on Tue Nov  8 13:53:27 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. currentmodule:: mumpce_new

Method of Uncertainty Minimization using Polynomial Chaos Expansions
====================================================================

*David A. Sheen*

*National Institute of Standards and Technology*

*Last Revision* |today|


`Download this software from GitHub <https://github.com/davidasheen/mumpce_py>`_
   
Welcome to the home page for the Method of Uncertainty Minimization using Polynomial Chaos Expansions (MUM-PCE). This software is a Python package that implements the methodology presented in `Sheen & Wang (2011) <http://dx.doi.org/10.1016/j.combustflame.2011.05.010>`_, `Wang & Sheen (2015) <http://dx.doi.org/10.1016/j.pecs.2014.10.002>`_, and `Sheen & Manion (2014) <http://dx.doi.org/10.1021/jp5041844>`_. The software does the following things:

  * Compiles a database of experimental measurements
  * Constrains a physical model against the measurements in the database (optimization)
  * Determines the uncertainty in the physical model parameters based on the uncertainty in the measurements (uncertainty analysis)
  * Identifies measurements that are inconsistent with the constrained model (outlier detection)
  * Identifies measurements that do not strongly constrain the constrained model (experimental design)

This implementation cannot be used out of the box. Instead, it is necessary for the user to create an interface to the user's own code, which will be specific to that application. Two examples of how to do this are provided. One is a toy model which demonstrates how an interface might be written; it is intended to be as complete as possible while also being simple. The other example is an interface to the reaction kinetics program Cantera; this sort of interface probably represents the worst use case possible, with multiple heterogeneous measurements and a highly complex interface to a detailed model.

The package is implemented in a way to be as general as possible, which means that efficiency is often sacrificed in order to implement this generality. Expert users may be able to modify the code in such a way as to make it more efficient for their particular application. No support is provided for this adventure, but please let me know if you are successful.

Legal
+++++

This software is subject to the NIST Software License (revised as of May 2015). This license can be found in the GitHub repo in the file named LICENSE. The following is a hopefully-useful but not-legally-binding summary:

  * NIST software authored by NIST employees is in the public domain (15 USC 105).
  * The software has NO WARRANTY.
  * You may modify the software and distribute your modifications. If you do, you should note your changes and cite the original.
  * If you use the software, you should cite the software and the papers documenting its development.

Contents
++++++++

.. toctree::
   :maxdepth: 2
   :includehidden:

   Project
   measurement
   toy
   cantera

Links
+++++

`GitHub profile <https://github.com/davidasheen>`_

`NIST GitHub Organization <https://github.com/usnistgov>`_

`NIST home page <http://nist.gov>`_



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

