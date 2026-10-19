# Yay, a Base Database to Do things!

This package provides computational workflow tools that build on top of the yabadaba package.

The basic functionality originates from iprPy. yabadabado allows for anyone to build their own methodologies and workflows for their own projects.

## Installation

Source code can be found at https://github.com/lmhale99/yabadabado

**BELOW DETAILS PLANNED INSTALLATION ONCE THE FIRST OFFICIAL RELEASE IS MADE!**

Install with pip
    pip install yabadabado
or conda
    conda install -c conda-forge yabadabado

Source code can be found at:
- https://github.com/usnistgov/yabadabado for official releases
- https://github.com/lmhale99/yabadabado for development 


## Documentation

A very brief overview guide is given below.  Full documentation is planned with the first official release of the package.  

### Calculations

Calculations are extensions of yabadaba Records. 

A Record manages data and data transformations associated with a single data record entry of a given schema. It interprets the data into Python attributes, specifies how to transform the data to and from XML and JSON formats, and can contain any custom functional capabilities that user may want for interacting with the data. Once a Record class is defined, the associated data can be easily added to and queried from a database.

A Calculation extends the base Record capabilities by also specifying how to interface with a calculation function. In particular, input values can be read in from a simple key-value text file, it generates the input parameters the calculation function expects, and processes the calculation function's outputs into class attribute values. This allows for a Calculation object to represent and manage a single run of a python "calculation" function.

At the bare minimum, a new Calculation class can be defined with three components:
- Calculation.calc should point to the primary calculation function to use. This should be defined by overriding the _init_calc(self) method and setting the self.calc value inside it. No restrictions are placed on what the calculation function does, but it is recommended that it returns a dict of named outputs for easy parsing of the generated results.
- A modelroot attribute needs to be defined that specifies the root element name to use for JSON/XML representations. Having a unique modelroot helps human and machine parsers in identifying what the record entry represents.
- Any Values for the class that are intended to be captured in the JSON/XML representations should be specified by overriding the _add_values(self) method.  This is the same as how yabadaba Record classes are defined. The main difference in yabadabado is that the value styles have been expanded to differentiate between calculation input values and result values.

Additional methods and attributes can be overridden to better support the design of multi-calculation workflows. These are described below.

### Input Values and Result Values

Yabadabado provides two new base Value classes InputValue and ResultValue, which extend the original base Value class. New subclasses are also defined that combine the new base class capabilities with the type-specific handling of the value subclasses defined in yabadaba.  For example, yabadabado defines new 'input_str' and 'result_str' value styles that extend the yabadaba-defined 'str' value style with the new capabilities.

Input values have additional components that dictate how to interpret the value from the key-value text input, and what input parameter(s) are to be passed to the calculation function.  Input values also have additional properties compare_term and compare_fterm indicating how they relate to the uniqueness of a given calculation run.
- compare_term is a boolean value, where True indicates that it is a value that influences calculation uniqueness and is a non-float value that can be directly compared.
- compare_fterm is a float value specifying the absolute tolerance to use for determining the uniqueness of a float value.

Result values have additional components that specify how to extract their corresponding values from the calculation function outputs.

There is also a new calculation subset value type that allows for the collection of common values that can be shared across multiple calculation styles.  This is primarily for complex input subsets but can also be used for standard output collections as well.

### Single calculation runs

Once a calculation has been defined as above, it can be executed in a few different ways.

- Within a Python environment, create a new instance of a Calculation by calling yabadabado.load_calculation().
  - Directly run the calculation function by interacting with the object's calc attribute.
  - Or, call the object's run() method to read in key-value parameters, run the calculation and build a results.json file.
- From the command line,
  - Call "yabadabado template {style}" to create an empty key-value input file for you to fill in.
  - Call "yabadabado run calc_{style}.in" to run the calculation based on the input parameter file.
  - When it finishes, a results.json should be generated.

### Iterative calculation runs

If you want to design your own simple low overhead workflows, you can do so by writing Python scripts that load one or more calculation styles and then run said calculations directly with calc or slightly indirectly with run().

If you want yabadabado to interface with a database to manage calculation preparation, execution, and collection keep reading.

#### Two step process: prepare and run

The yabadabado workflow tools divide the execution of calculation workflows into two primary steps: prepare and run.
- The prepare step generates new calculation runs that are intended to be executed. It iterates over input combinations for a calculation, checks if the proposed new runs are valid and unique wrt records in a database, creates a key-value text input for each new run, and adds an associated placeholder record into the database.
- The run step executes one or more prepared calculations. If it finishes successfully, the result outputs are added to the associated database record. If it issues an error, the error message is added to the associated database record. Any generated datafiles are also archived into the database. The standard "runner" operations sequentially run all calculations in a given folder, and multiple runners can operate in the same folder without issue.

#### Prepare

At the most basic level, prepare operates according to the following rules

1. Single runs of a given calculation are based on key-value text inputs in which each key is allowed only one full and complete value. 
2. Iterative prepares then can be defined based on similar key-value text inputs in which multiple values are given for the same key to iterate over.
3. *However*, not all iterative combinations may be meaningful or useful to run! To handle this, the Calculation class can define extra components
    - singularkeys is a list of the input keys that should only have one value, i.e. it is not meaningful to iterate over them.
    - multikeys is a list of lists, in which each internal list collects a subset of input keys that should be iterated over together rather than independently. This helps avoid generating meaningless input value combinations.
    - isvalid() defines a check on the calculation's input values to verify that they are associated with a meaningful calculation. You can use this to catch any invalid combinations that may still occur.

The basic level above allows for manually specifying iterative combinations, but if we are working with a database we can do better and have it figure out combinations for itself.  This is done through the use of buildcombos functions. Each buildcombos function specifies how to query a database, identify parent records to use, and generate all values of a multikeys subset based on the parent records. Once a buildcombos function is defined and incorporated into yabadabado, it can be identified and used inside the prepare input content. The basic prepare script and buildcombos functions are enough to set up simple workflows of a small number of different calculation styles.

For more complex workflows that involve a very large number of runs of a single calculation style and/or multiple different calculation styles, it is recommended to use "master_prepare" instead. The master_prepare provides a higher-level interface for prepare based on
1. Defining a master_prepare_inputs() method inside a Calculation class definition that outlines default input values to use for the calculation based on a "branch".  Multiple branches can be defined allowing for separate specification of conflicting input sets and/or using the calculation differently based on its location inside a multi-calculation workflow.
2. Calling master_prepare() with a simpler input script that only specifies
    - which calculations to use, where to prepare them, how many cores,
    - required values for the calculations, and 
    - optionally overriding values for any of the calculation branch's default values.

The iprPy package that yabadabado spawned from also has Emperor and Commander scripts for managing calculation workflows.  These build on master_prepare for managing full calculation workflows. They are not included in yabadabado as they are workflow-specific.

#### Running

blahhhhh!!!!!!!!!!