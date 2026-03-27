This is the abstract class of the ```pyMANGA.ResourceLib```.

# Information for developers 
## Structure of each Resource module

Each resource module must contain the following methods:

- ``prepareNextTimeStep(self, t_ini, t_end)``: Prepares next time step by initializing relevant variables.
- ``addPlant(self, plant)``: Adds each plant and its relevant geometry and parameters to the object to be used in the next time step.
- One of: ``calculateAbovegroundResources(self)`` or ``calculateBelowgroundResources(self)``: Calculates and sets the resource factor of each plant.

## ResourceModel

This class contains getter functions which are accessed by ``pyMANGA.TimeLoopLib``.

### getAbovegroundResources

Returns a list of length = number of plants indicating the above-ground resource availability of each plant.

### getBelowgroundResources

Returns a list of length = number of plants indicating the below-ground resource availability of each plant.

### superordinate methods

This library also contains superordinate functions that can be used by all resource moduls such as:

#### getInputParameters

Reads and processes the specifications provided in the project file relevant for the chosen resource module.

The ``tags`` dictionary supports the following keys:

- ``prj_file``: XML element containing module parameters
- ``required``: list of required tag names
- ``optional``: list of optional tag names
- ``case_insensitive``: (optional) list of tag names whose string values should be converted to lowercase. Tags not in this list preserve their original case. Use this for enum-like parameters (e.g. ``backend_type``) but not for file paths.

#### makeGrid

Create a regular grid that extends a rectangle of size x*y, where
```python
x = x_2 - x_1
y = y_2 - y_1
```
and the size of each cell is
and cell size of
````python
xs = x_2 / x_resolution
ys = y_2 / y_resolution
````


---

