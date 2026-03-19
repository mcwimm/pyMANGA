
PYthon Models for AGeNt-based resource GAthering (pyMANGA) is a collection of models describing vegetation population dynamics from first principles.
pyMANGA is modular, and descriptions of individual tree growth, resource availability and competition dynamics can be quickly interchanged.

### Structure of pyMANGA documentation
The source code is divided into seven libraries, organized by purpose: ProjectLib, TimeLoopLib, PopulationLib, PlantModelLib,
ResourceLib, ModelOutputLib, VisualizationLib (left navigation bar). A library may contain several modules, each representing a different
realization of the overarching library purpose.

The documentation for each module follows the structure below:
1. **Description**: Short description of the module
2. **Usage**: Specification of the tags to be used in the pyMANGA project XML file (if applicable)
3. **Attributes**: Input parameters of the module
4. **Value**: Return value of the module
5. **Details**: A detailed description of the module, explaining its purpose and processes, and  listing notes on its applications and restrictions
6. **Examples**: Extends the usage by providing more examples of how to use this module


*Note*
All parameters are defined in SI units unless indicated otherwise.

### Further information

- For general information about the pyMANGA project and tutorials visit our <a target="_blank" href="http://pymanga.forst.tu-dresden.de/">website</a>
- To learn more about model structure read <a target="_blank" href="https://doi.org/10.1016/j.envsoft.2024.105973">Wimmler et al. 2024</a>
- Find the source code on <a target="_blank" href="https://github.com/pymanga/pyMANGA">GitHub</a>
- Problems? <a target="_blank" href="https://github.com/pymanga/pyMANGA/issues/new">File an Issue</a>

### How to cite pyMANGA

When using pyMANGA, please:
- Cite the specific version used in all publications  
- Clearly disclose any modifications in the methods section  
- Seek verification for new features intended for production use  


The table below provides guidance on how to cite pyMANGA depending on your type of usage.

| Case                                          | Description | Example citation                                                                                                                                                                                                                                                                                                                                                                                 |
|-----------------------------------------------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1 – Standard usage**                        | Use of pyMANGA without any modifications. | *"We used pyMANGA (version [INSERT <a target="_black" href="https://github.com/pymanga/pyMANGA/releases">VERSION TAG</a>]) without modifications (Optional: <a target="_blank" href="https://doi.org/10.1016/j.envsoft.2024.105973">Wimmler et al. 2024</a>)."* |
| **2 – Modified usage (not verified)**       | Use of pyMANGA with custom modifications that have **not been verified** by the pyMANGA team. | *"We used pyMANGA (version [INSERT <a target="_black" href="https://github.com/pymanga/pyMANGA/releases">VERSION TAG</a>]) with custom modifications to [briefly describe components/modules]. These changes have not been verified by the pyMANGA team. Details are in [Methods/Supplementary Material]."*     |
| **3 – Extended usage with verified features** | Use of pyMANGA including features that are part of an official release (i.e. **verified and integrated**). | *"We used pyMANGA (version [INSERT <a target="_black" href="https://github.com/pymanga/pyMANGA/releases">VERSION TAG</a>]), which includes verified new features described in [Methods/Supplementary Material] and incorporated into the pyMANGA documentation (https://pymanga.github.io/pyMANGA).*"                                                                                                       |


### CoreTeam

@<a target="_blank" href="https://github.com/mcwimm">mcwimm</a>
@<a target="_blank" href="https://github.com/jbathmann">jbathmann</a>
@<a target="_blank" href="https://github.com/jvollhueter">jvollhueter</a>

