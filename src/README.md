Repository for the SAFtool toolflow. This toolflow consumes a package of [Sparseloop](https://sparseloop.mit.edu/) configuration files. The toolflow outputs a modified configuration package which integrates SAF microarchitecture (SAF uarch) modeling.

* **SAFinfer** - infer a high-level uarch description for each SAF in the Sparseloop config
* **SAFmodel** - compile the high-level uarch description into a set of pre-RTL (Accelergy) models of SAF uarch costs
* **SAFarch** - modify the architecture specification in the Sparseloop config to utilize SAF uarch models