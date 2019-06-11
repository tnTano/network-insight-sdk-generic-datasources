import importlib


def load_class(class_path):
    module = importlib.import_module(".".join(class_path.split('.')[:-1]))
    class_name = class_path.split('.')[-1]
    return getattr(module, class_name)


def load_class_method(class_object, function_name):
    return getattr(class_object, function_name)


def load_block_parser(class_name):
    module = importlib.import_module(
        "{}".format(".".join("network_insight_sdk_generic_datasources/parsers/common/block_parser".split('/'))))
    return getattr(module, class_name)


def load_device_pre_post_parser(device, class_name):
    module_path = "{}.{}.{}_{}".format("network_insight_sdk_generic_datasources", device, device, "pre_post_processor")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)