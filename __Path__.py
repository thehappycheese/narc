import os

import arcpy
import __thou_shalt__
from .__thou_shalt__ import thou_shalt
from .__sanitize_feature_class_name__ import sanitize_feature_class_name


class ARCPY_DATA_TYPE:
	Workspace = "Workspace"
	FeatureClass = "FeatureClass"
	Table = "Table"
	Layer = "Layer"

class Path(object):
	
	"""Represents an ArcPy data element or geoprocessing object"""
	
	def __init__(self, *args):
		self._path = ""
		self._desc = None
		for item in args:
			self._path = os.path.join(self._path, str(item))
	
	def arcpy_exists(self):
		return arcpy.Exists(self._path)
	
	def arcpy_describe(self):
		if self._desc is None:
			self._desc = arcpy.Describe(self._path)
		return self._desc
	
	def append(self, new_path_part):
		'''in place append to path'''
		self._path = os.path.join(self._path, new_path_part)
		self._desc = None
		return self
	
	@property
	def desc(self):
		return self.arcpy_describe()

	def folder(self):
		return self.desc.baseName

	def filename(self):
		return self.desc.file
	
	def name(self):
		"""user assigned name"""
		return self.desc.file
	
	def path(self):
		"""including filename / geodatabase name and extentnion"""
		return self.desc.catalogPath
	
	def children(self):
		return [Path(item.catalogPath) for item in self.desc.children]
	
	def data_type(self):
		return self.desc.dataType
	
	def is_workspace(self):
		return self.data_type() == ARCPY_DATA_TYPE.Workspace

	def is_feature_class(self):
		return self.data_type() == ARCPY_DATA_TYPE.FeatureClass

	def shortened_name_with_context(self):
		if self.is_workspace():
			return self.filename()
		elif self.is_feature_class():  # TODO: assumes feature classes are always inside a geodatabase
			# return the path upto and including the partne geodatabase "some.gdb\\folder\\featureclass"
			d = self._path.split("\\")
			try:
				ds = next(index for index, value in enumerate(d) if value[-4:] == ".gdb")
			except StopIteration:
				ds = -2
			return "\\".join(d[ds:])
		else:
			d = self._path.split("\\")
			if len(d) > 1:
				# return everything up to the containing folder; "folder\\featureclass"
				return "\\".join(d[-2:])
			else:
				# or if the item is not in a folder simply the name of the item
				return self.filename()

	
	
	
	
	def arcpy_delete(self):
		if self.arcpy_exists():
			thou_shalt(
				"Delete "+self.filename(),
				lambda: arcpy.Delete_management(self._path)
			)
		return self
	
	def arcpy_create_gdb(self):
		thou_shalt(
			"Create Geodatabase "+self.filename(),
			lambda:arcpy.CreateFileGDB_management(self.folder(),self.filename())
		)
		return self

	def arcpy_select_to(self, arg_output_path, where_clause):
		arg_output_path = Path(arg_output_path)
		thou_shalt(
			"Select from\n\t\t%s into\n\t\t%s\n\t\twhere %s"%(self.shortened_name_with_context(),arg_output_path.shortened_name_with_context(),where_clause),
			lambda:arcpy.Select_analysis(self._path,str(arg_output_path),where_clause=where_clause)
		)
		return self

	def arcpy_select_from(self, arg_input_path, where_clause):
		arg_input_path = Path(arg_input_path)
		thou_shalt(
			"Select from\n\t\t%s INTO\n\t\t%s WHERE\n\t\t%s"%(arg_input_path.shortened_name_with_context(),self.shortened_name_with_context(),where_clause),
			lambda:arcpy.Select_analysis(str(arg_input_path), str(self), where_clause=where_clause)
		)
		return self
	
	def arcpy_intersect_from(self, arg_list_paths, cluster_tolerance=None, output_type="INPUT"):
		''' Always joins ALL attributes
		input_type can be INPUT(default),LINE or POINT
		Ranks by list order by default (features ealier in the list will snap to features later in the list).
		Otherwise provide custom ranks (ie [[feature,rank],[feature,rank],...]) where ranks are integer literals from 1 to 50 with features snapping to higher numbers'''
		
		auto_rank = True
		if type(arg_list_paths[0]) is list:
			auto_rank = False

		features_in = [[value,index+1] for index,value in list(enumerate(map(str,arg_list_paths)))] if auto_rank else map(str,arg_list_paths)
		print_string = [[value,index+1] for index,value in list(enumerate(map(lambda item: Path(item).shortened_name_with_context(),arg_list_paths)))] if auto_rank else map(str,arg_list_paths)
		thou_shalt(
			"Intersect [%s] with tollerance %s into %s"%(",".join(map(str,print_string)),str(cluster_tolerance),self.shortened_name_with_context()),
			lambda:arcpy.Intersect_analysis(features_in,self._path,join_attributes="ALL",cluster_tolerance=cluster_tolerance,output_type=output_type)
		)
		return self
		
	def arcpy_clip_to(self, clip_features, arg_output_path, cluster_tolerance=None):
		# TODO: if the user has passed in vanilla string paths as arguments... we sould make sure they are real paths or the .filename() call below will fail
		arg_output_path = Path(arg_output_path)
		clip_features = Path(clip_features)
		thou_shalt(
			"Clip %s using %s into %s" % (self.filename(), clip_features.filename(), arg_output_path.filename()),
			lambda: arcpy.Clip_analysis(str(self), str(clip_features), str(arg_output_path), cluster_tolerance)
		)
		return self

	def arcpy_buffer_to(self, arg_output_path, buffer_distance_or_field="20 Meters", dissolve_option="ALL"):
		arg_output_path = Path(arg_output_path)
		thou_shalt(
			"Buffer %s by %s into %s"%(self.filename(), buffer_distance_or_field, arg_output_path.filename()),
			lambda: arcpy.Buffer_analysis(str(self), str(arg_output_path), buffer_distance_or_field, dissolve_option=dissolve_option)
		)
		return self

	def arcpy_dissolve_to(self, arg_output_path, dissolve_field, unsplit_lines="UNSPLIT_LINES"):
		arg_output_path = Path(arg_output_path)
		thou_shalt(
			"Dissolve\n\t\t%s into\n\t\t%s by field \n\t\t%s with \n\t\tunsplit_lines=%s" % (self.filename(), arg_output_path.filename(), dissolve_field, unsplit_lines),
			lambda: arcpy.Dissolve_management(str(self), str(arg_output_path), dissolve_field, unsplit_lines="UNSPLIT_LINES")
		)
		return self
	
	def arcpy_to_feature_class(self, arg_output_path, where_clause=None, field_mapping=None, config_keyword=None):
		arg_output_path = Path(arg_output_path)
		thou_shalt(
			"Create feature class from\n\t\t%s at \n\t\t%s"%(self.shortened_name_with_context(), arg_output_path.shortened_name_with_context()),
			lambda: arcpy.FeatureClassToFeatureClass_conversion(self._path, arg_output_path.folder(), arg_output_path.filename(), where_clause, field_mapping, config_keyword)
		)
		return self

	def arcpy_get_unique_field_values(self,arg_field_name):
		"""Extract sorted list of unique values from a chosen field"""
		# next line uses python 'set comprehension'... basically an inline for-loop which defines the elements of the set.
		# Sets automatically only retain one of each unique item (as youmight expect)
		# A Set is like a dictionary (hence the curley braces), except instead of {key:value,key:value,...} it is just {key,key,...}
		if __thou_shalt__.do_a_dry_run:
			return [1]
		return thou_shalt("Extract sorted list of unique values from \n\t\tfield %s of \n\t\t%s"%(arg_field_name,self.shortened_name_with_context()),
			lambda: sorted(list({cursor.getValue(arg_field_name) for cursor in arcpy.SearchCursor(str(self))}))
		)
	
	def arcpy_get_number_of_rows(self):
		if __thou_shalt__.do_a_dry_run:
			return 1
		return thou_shalt("Count rows of %s"%(self.shortened_name_with_context()),
			lambda:int(arcpy.GetCount_management(str(self)).getOutput(0))
		)
	
	def arcpy_add_field(self, field_name, field_type):
		thou_shalt("Add field\n\t\t'%s' to\n\t\t%s" % (field_name, self.shortened_name_with_context()),
			lambda: arcpy.AddField_management(str(self), field_name, field_type)
		)
		return self

	def arcpy_alter_field(self,field, new_field_name=None, new_field_alias=None, field_type=None, field_length=None, field_is_nullable=None, clear_field_alias=None):
		thou_shalt("Alter Field {} of {}".format(field, self.shortened_name_with_context()),
			lambda: arcpy.AlterField_management(str(self), field, new_field_name, new_field_alias, field_type, field_length, field_is_nullable, clear_field_alias)
		)
		return self
	def arcpy_rename(self,new_filename):
		"""DONT THINK THIS WORKS? only tested on im_memory object... didnt like it"""
		# TODO: fix this
		old_name = self.shortened_name_with_context()
		old_path = self._path
		self._path = os.path.join(self.folder(), new_filename)
		thou_shalt("Rename\n\t\t{} to\n\t\t{}".format(old_name, self.shortened_name_with_context()),
			lambda:arcpy.Rename_management(old_path, new_filename)
		)
		
	def arcpy_get_field_objects(self):
		"""returns list of "Field" objects"""
		if __thou_shalt__.do_a_dry_run:
			return []
		return thou_shalt("Fetch field information from {}".format(self.shortened_name_with_context()),
			lambda:arcpy.ListFields(str(self))
		)

	def arcpy_get_field_names(self):
		"""returns list of strings"""
		info = self.arcpy_get_field_objects()
		return map(lambda item: item.name, info)
	
	def arcpy_get_field_types_for_pandas(self):
		"""returns list of strings"""
		fnames = self.arcpy_get_field_names()
		npa = arcpy.da.TableToNumPyArray(str(self), fnames, null_value=-999)
		output = []
		for fnm in fnames:
			output.append(str(npa.dtype[fnm]))
		return output

	def arcpy_prefix_field_names(self, prefix):
		names = self.arcpy_get_field_names()
		safe_prefix = sanitize_feature_class_name(prefix)

		def arcpy_call():
			for name in names:
				if name == "OID" or name == "Shape":
					continue
				# new_name = (safe_prefix + name)[:10]
				new_name = safe_prefix + name
				arcpy.AlterField_management(str(self), name, new_name),
		thou_shalt("Prefix fields of \n\t\t{}\n\t\twith '{}'".format(self.shortened_name_with_context(), safe_prefix),
			arcpy_call
		)

	def arcpy_fill_column_with_value(self, field_name, arg_value):
		def populate_column(field_name, arg_value):
			with arcpy.da.UpdateCursor(str(self),[field_name]) as cursor:  # pylint: disable=no-member
				for row in cursor:
					row[0] = arg_value
					cursor.updateRow(row)
		thou_shalt("Populate column %s of %s with value %s"%(field_name, self.shortened_name_with_context(), str(arg_value)),
			lambda: populate_column(field_name, arg_value)
		)
	
	def arcpy_execute_on_fields_all_rows(self, lambda_process_row, field_name_list):
		# TODO: probably untested
		def arcpy_call(field_name_list, lambda_process_row):
			field_dict = {name: index for index, name in enumerate(field_name_list)}
			with arcpy.da.UpdateCursor(str(self), field_name_list) as cursor:  # pylint: disable=no-member
				for row in cursor:
					lambda_process_row(row, cursor, field_dict)
					cursor.updateRow(row)
		thou_shalt("Execute code on column list %s of %s" % (str(field_name_list), self.shortened_name_with_context()),
			lambda: arcpy_call(field_name_list, lambda_process_row)
		)

	def arcpy_append_features(self, input_features_list):
		if type(input_features_list) is str or type(input_features_list) is Path:
			input_features_list = [input_features_list]
		input_features_list = map(Path, input_features_list)
		thou_shalt("Append features from  %s to %s" % (str([item.shortened_name_with_context() for item in input_features_list]), self.shortened_name_with_context()),
			lambda: arcpy.Append_management([str(item) for item in input_features_list],str(self))
		)
	
	def arcpy_create_routes_linear_refernancing_from(self, arg_input_path, segment_identifier_column="NETWORK_ELEMENT", start_column="START_TRUE_DIST", end_column="END_TRUE_DIST"):
		arg_input_path = Path(arg_input_path)
		thou_shalt("Create Linear Referanceable Layer {} from {}".format(self.shortened_name_with_context(), arg_input_path.shortened_name_with_context()),
			lambda: arcpy.CreateRoutes_lr(str(arg_input_path), segment_identifier_column, str(self), "TWO_FIELDS", start_column, end_column)
		)
		return self
		
	def arcpy_get_in_memory_version(self, where=None):
		"""returns a Path() object pointing to an in_memory version of this Path"""
		in_memory_path = Path("in_memory", self.filename())
		thou_shalt("Move to in_memory \n\t\t{} as {}".format(self.shortened_name_with_context(), self.filename()),
			lambda: arcpy.FeatureClassToFeatureClass_conversion(str(self), in_memory_path.folder(), in_memory_path.filename(), where)
		)
		return in_memory_path
	
	def arcpy_save_attributes_as_CSV(self,output_path):
		fields = self.arcpy_get_field_names()
		nparr = arcpy.da.FeatureClassToNumPyArray(str(self), fields)

	def __str__(self):
		return self._path
	
	def __add__(self, other):
		return Path.from_join(self._path, Path(other)._path)

	def __radd__(self, other):
		if type(other) is str:
			return other + self._path
		if type(other) is Path:
			return Path.from_join(other._path, self._path)

	def __repr__(self):
		return "<narc.Path %s>"%self._path
	
	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.arcpy_delete()
	
	@classmethod
	def from_join(_class,str_folder,str_filename):
		return _class(os.path.join(str(str_folder),str(str_filename)))