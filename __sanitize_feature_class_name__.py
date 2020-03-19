import re
regex_sanitise_feature_class_name = re.compile("[^A-z0-9_]")
def sanitize_feature_class_name(arg_str):
    return regex_sanitise_feature_class_name.sub("_",arg_str)