import ast
import os


def assert_Store(ast_) -> bool: return isinstance(ast_, ast.Store)
def assert_Load(ast_) -> bool: return isinstance(ast_, ast.Load)
def assert_keyword(ast_) -> bool: return isinstance(ast_, ast.keyword)
def assert_Assign(ast_) -> bool: return isinstance(ast_, ast.Assign)
def assert_Call(ast_) -> bool: return isinstance(ast_, ast.Call)
def assert_ClassDef(ast_) -> bool: return isinstance(ast_, ast.ClassDef)


class MakeDoc:
    def __init__(self, walk_dir: str):
        self.walk_dir = walk_dir

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
                            "member_verbose_name": "Not set"
                        })
        model_class_membres_dict.setdefault(class_name, model_class_members)
        return model_class_membres_dict

    def get_doc__file(self, file):
        with open(file, "r") as f:
            p = ast.parse(f.read())
            # get all classes from the given python file.(models.py)
            classes = [_class for _class in ast.walk(
                p) if assert_ClassDef(_class)]
            print(self.get_doc__class(classes[0]))

    def get_doc_dir(self):
        pass



