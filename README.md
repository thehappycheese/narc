# NARC: Nick's ArcPy (10.5) Wrapper Library

Wrap arcpy feaure classes, geodatabases, tables etc as a python object for syntactic sugar purposes.

At this stage the library is in very early stages and only wraps a small number of arcpy functions.
The **\_\_thou_shalt\_\_.py** module is intended as a way to deal with file locks; it will keep trying to run an arcpy command untill you close arcmap for example and the file lock is removed, rather than simply aborting the entire script. This is of limited use at the moment, but i am 

instead of 
~~~python
import arcpy
arcpy.some_tool("<somepathto_featureclass>","<somepath_to_gdb_workspace>", *args, **kwargs)
~~~

we do
~~~python
import narc
featureclasspath = narc.Path("<somepathto_featureclass>")
workspacepath = narc.Path("<somepath_to_gdb_workspace>")

featureclasspath.some_tool(workspacepath, *args, **kwargs)
~~~

This allows refactoring of object names, and composition of paths for maintenance of sanity;
~~~python
import narc

workspacepath = narc.Path("C:/workspace.gdb")
featureclasspath1 = narc.Path(workspacepath, "my_points")
featureclasspath2 = narc.Path(workspacepath, "my_lines")
~~~