This repository contains datacenter network and WAN benchmark examples in ACORN_IR format. For the datacenter examples, we also provide benchmarks in  NV format and ShapeShifter format (Cisco configurations). Due to file size limits, we provide a few datacenter examples (compressed); additional examples can be generated using the provided scripts. 

`ex1.in` is a small example network in ACORN_IR format. `ir.py`, `routemap.py`, and `util.py` are dependencies of the scripts that generate datacenter benchmark examples. 

To generate a benchmark to check reachability in a FatTree network with parameter 10 (125 nodes) running the valley-free policy, run the following command from the `ACORN_benchmarks` directory:  

`python3 -m datacenter.valley-free.fattree_vf 10 reach-singlesrc`

