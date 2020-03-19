# NARC: Nick's ArcPy (10.5) Wrapper Library

Wrap arcpy feaure classes, geodatabases, tables etc as a python object for syntactic sugar purposes.

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


featureclasspath.some_tool(workspacepath, *args, **kwargs)
~~~