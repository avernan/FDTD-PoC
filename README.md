# FDTD-PoC
A minimal FDTDPoC proof of concept.
The aim of the project is to implement a simple FDTDPoC solver in python3,
and use it to help people familiriarize with the workings of the
algorithm. To this aim, the solver should work in 2D (for TE and/or TM
polarisations) and allow for easy configuration of a TFSF plane wave
source as well as simple geometries. A real time animation could also
have a good teaching impact.

It has the following features:

* Fill me in, please :(

## Dependencies

The code has been written on Linux (Ubuntu 17.10) using python3.
Packages required:

* `numpy`
* `matplotlib`

## TODO

List of desired features:

* engine
    1. Working 2D solver (TE/TM)
    1. Absorbing boundaries (PML)
    1. Dielectrics (arbitrary refractive index)
    1. Metals (Drude model) (default materials)
    1. Two level systems (?)
    1. TFSF source
    1. ...
* GUI and data presentation
    1. Real time field animation
    1. Easy geometry definition
    1. Real time (?) DFT/FFT
    1. Real time envelope extraction (Hilbert transform)
    1. ...

This looks ambitious!

## Virtual environment set up

[Look here](http://docs.python-guide.org/en/latest/dev/virtualenvs/#lower-level-virtualenv)