import ast
import os

django_models_fields = ['AutoField', 'BigAutoField', 'BigIntegerField', 'BinaryField', 'BooleanField', 'CharField', 'DateField', 'DateTimeField', 'DecimalField', 'DurationField', 'EmailField', 'FileField', 'FilePathField', 'FloatField', 'GenericIPAddressField', 'IPAddressField',
                        'ImageField', 'IntegerField', 'JSONField', 'PositiveIntegerField', 'PositiveBigIntegerField', 'PositiveSmallIntegerField', 'SlugField', 'SmallAutoField', 'SmallIntegerField', 'TextField', 'TimeField', 'URLField', 'UUIDField', 'ForeignKey', 'ManyToManyField', 'OneToOneField']

django_models_fields_desc = [
    "An IntegerField that automatically increments according to available IDs",
    "A 64-bit integer, much like an AutoField except that it is guaranteed to fit numbers from 1 to 9223372036854775807.",
    "A 64-bit integer, much like an IntegerField except that it is guaranteed to fit numbers from -9223372036854775808 to 9223372036854775807",
    "A field to store raw binary data. It can be assigned bytes, bytearray, or memoryview.",
    "A true/false field.",
    "A string field, for small- to large-sized strings.",
    "A date, represented in Python by a datetime.date instance",
    "A date and time, represented in Python by a datetime.datetime instance",
    "A fixed-precision decimal number, represented in Python by a Decimal instance",
    "A field for storing periods of time - modeled in Python by timedelta",
    "A CharField that checks that the value is a valid email address using EmailValidator.",
    "A file-upload field.",
    "A CharField whose choices are limited to the filenames in a certain directory on the filesystem.",
    "A floating-point number represented in Python by a float instance.",
    "An IPv4 or IPv6 address, in string format (e.g. 192.0.2.30 or 2a02:42fe::4).",
    "An IPv4 or IPv6 address, in string format (e.g. 192.0.2.30 or 2a02:42fe::4).",
    "An IPv4 or IPv6 address, in string format (e.g. 192.0.2.30 or 2a02:42fe::4).",
    "Inherits all attributes and methods from FileField, but also validates that the uploaded object is a valid image.",
    "An integer. Values from -2147483648 to 2147483647 are safe in all databases supported by Django.",
    "A field for storing JSON encoded data.",
    "Values from 0 to 2147483647",
    "Values from 0 to 9223372036854775807",
    "Values from 0 to 32767",
    "A slug is a short label for something, containing only letters, numbers, underscores or hyphens",
    "Values from -32768 to 32767",
    "A large text field.",
    "A time, represented in Python by a datetime.time instance.",
    "A CharField for a URL, validated by URLValidator.",
    "A field for storing universally unique identifiers. Uses Python’s UUID class",
    "A many-to-one relationship. Requires two positional arguments: the class to which the model is related and the on_delete option",
    "A many-to-many relationship",
    "A one-to-one relationship. Conceptually, this is similar to a ForeignKey with unique=True, but the “reverse” side of the relation will directly return a single object."
]
all_models_fields_types_desc = dict(
    zip(django_models_fields, django_models_fields_desc))


def assert_Store(ast_) -> bool: return isinstance(ast_, ast.Store)
def assert_Load(ast_) -> bool: return isinstance(ast_, ast.Load)
def assert_keyword(ast_) -> bool: return isinstance(ast_, ast.keyword)
def assert_Assign(ast_) -> bool: return isinstance(ast_, ast.Assign)
def assert_Call(ast_) -> bool: return isinstance(ast_, ast.Call)
def assert_ClassDef(ast_) -> bool: return isinstance(ast_, ast.ClassDef)


class MakeDoc:
    def __init__(self, walk_dir: str):
        self.walk_dir = walk_dir

    def set_doc__class(self, _class_membres_dict: dict) -> str:
        def formatted_class_member(s): return "\n".join([s.get(
            "member_name") + " : "+s.get("member_type"), s.get('member_verbose_name')])
        
        formatted_class = '\n'.join([formatted_class_member(
            member) for member in list(_class_membres_dict.values())[0]])
        
        return f"""
                Attributes
                ----------
                {formatted_class}
            """

    def set_doc__files(self, _class_membres_dict: dict) -> str:
        return ""

    def set_doc__dir(self, _class_membres_dict: dict) -> str:
        return ""

    def get_doc__class(self, _class: ast.ClassDef) -> dict:

        membres_list = [xx for xx in ast.walk(_class) if assert_Assign(xx)]
        model_class_membres_dict = {}
        class_name = _class.name
        # Assign(expr* targets, expr value, string? type_comment)
        model_class_members = []
        for member in membres_list:
            _member = ast.parse(member)
            assign_targets_Name_ctx = _member.targets[0].ctx
            # Call(expr func, expr* args, keyword* keywords)
            # member_name == member[targets].Name.id if member[targets].Name.ctx == Store()
            if assert_Call(_member.value) and assert_Store(assign_targets_Name_ctx):
                # assert that is a models field .. for models.py file
                if _member.value.func.value.id == 'models' and assert_Load(_member.value.func.value.ctx):
                    # class member name
                    assign_targets_Name_id = _member.targets[0].id
                    call_keywords = _member.value.keywords
                    # we get the `verbose_name` if exist else we set other documentation
                    verbose_exist_or_not = [keyword for keyword in call_keywords if keyword.arg ==
                                            "verbose_name" and assert_keyword(keyword)]
                    if len(verbose_exist_or_not):
                        model_class_members.append({
                            "member_name": assign_targets_Name_id,
                            "member_type": _member.value.func.attr,
                            "member_verbose_name": verbose_exist_or_not[0].value.value
                        })
                    else:
                        model_class_members.append({
                            "member_name": assign_targets_Name_id,
                            "member_type": _member.value.func.attr,
                            "member_verbose_name": all_models_fields_types_desc.get(_member.value.func.attr)
                        })
        model_class_membres_dict.setdefault(class_name, model_class_members)
        return model_class_membres_dict

    def get_doc__file(self, file):
        with open(file, "r") as f:
            p = ast.parse(f.read())
            # get all classes from the given python file.(models.py)
            classes = [_class for _class in ast.walk(
                p) if assert_ClassDef(_class)]
            print(self.set_doc__class(self.get_doc__class(classes[0])))

    def get_doc_dir(self):
        pass


makeDoc = MakeDoc("/")


