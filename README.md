# Graph_Validations

Graph_Validations is package that contains 
functions for checking if Schematic Editor graphs contained in JSON file are built correctly

Graph_Validations is fully implemented in Python.

## Installation

You can use `pip` to install Graph_Validations:

```
$ pip install graph_validations
```

To verify that you have installed Silvera correctly run the following command:

```
$ graph_validations
```

You should get output like this:

```
Usage: graph_validations [OPTIONS] COMMAND [ARGS]...        
                                                            
Options:                                                    
  --debug  Debug/trace output.                              
  --help   Show this message and exit.                      
                                                            
Commands:                                                   
  validate-graph   Checks if the given graph is valid.      
  validation-list  Lists all currently available validations
```

## Python versions

Tested with Python 3.7.4+