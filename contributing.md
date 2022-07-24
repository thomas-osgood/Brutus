# Contributing Guidelines

## Function Names

- Function names shall be descriptive and give a basic idea of what the function does.
- Function names shall be all lowercase.
- Spaces in function names shall be replaced with underscores (_).

### Examples

Good:
```
def get_index_page(target)
```

Bad:
```
def function1(target)
```

## Function Structure

### Docstring

All functions shall have a docstring with the same basic layout. This will provide a clear description to the end-user of what the function does and how to call it. Additionally, this allows the function to be viewed in the "help" funciton in Python's interactive mode.

Format:
```
"""
Function Name:
	<name>
Author:
	<author>
Description:
	<short description here>
Input(s):
	<function input(s)>
Return(s):
	<function return(s)>
"""
```
