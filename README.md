# FDTD-PoC
A minimal FDTD proof of concept (FDTDPoC).
The aim of the project is to implement a simple FDTD solver in python3,
and use it to help people familiriarize with the workings of the
algorithm. To this aim, the solver should work in 2D (for TE and/or TM
polarisations) and allow for easy configuration of a TFSF plane wave
source as well as simple geometries. A real time animation could also
have a good teaching impact.

It has the following features:

* Additive dipolar sources can be added at arbitrary positions
    * An independent `pulse` component representing the time dependence of the source
* Reflective boundaries through perfect electric conductor (PEC)
* Absorptive (i.e. open system) boundaries through absorbing boundary conditions (ABC)

## Dependencies

The code has been written on Linux (Ubuntu 17.10) using python3.
Packages required:

* `numpy`

Packages required to run the test driver:

* `matplotlib`

## TODO

List of desired features for the FDTD solver

1. Working 2D solver (TE/~~TM~~)
1. Boundaries
    * Absorbing boundaries (~~ABC~~/PML)
    * ~~Reflecting boundaries (PEC)~~
1. Sources
    * ~~Dipolar additive source~~
    * TFSF box
1. Materials
    * Dielectrics (arbitrary `n`)
    * Metals (Drude model)
    * Two level system (?)
1. ...

and the GUI and data analysis/presentation

1. Real time field animation
1. Easy geometry definition
1. Real time (?) DFT/FFT
1. Real time envelope extraction (Hilbert transform)
1. ...

This looks ambitious!

## Virtual environment set up

[Look here](http://docs.python-guide.org/en/latest/dev/virtualenvs/#lower-level-virtualenv)