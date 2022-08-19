import ast

def assert_Store(ast_): return isinstance(ast_, ast.Store)
def assert_Load(ast_): return isinstance(ast_, ast.Load)
def assert_keyword(ast_): return isinstance(ast_, ast.keyword)
def assert_Assign(ast_): return isinstance(ast_, ast.Assign)
def assert_Call(ast_): return isinstance(ast_, ast.Call)
def assert_ClassDef(ast_): return isinstance(ast_, ast.ClassDef)


def get_doc__class(_class: ast.ClassDef) -> dict:

    membres_list = [xx for xx in ast.walk(
        _class) if assert_Assign(xx)]
    membres_dict = {}
    # Assign(expr* targets, expr value, string? type_comment)
    for member in membres_list:
        _member = ast.parse(member)
        assign_targets_Name_ctx = _member.targets[0].ctx
        # Call(expr func, expr* args, keyword* keywords)
        # member_name == member[targets].Name.id if member[targets].Name.ctx == Store()
        if assert_Call(_member.value) and assert_Store(assign_targets_Name_ctx):
            # assert that is a models field .. for models.py file
            if _member.value.func.value.id == 'models' and assert_Load(_member.value.func.value.ctx):

                # print(ast.dump(_member))
                # class member name
                assign_targets_Name_id = _member.targets[0].id
                call_keywords = _member.value.keywords
                # we get the `verbose_name` if exist else we set other documentation
                verbose_exist_or_not = [keyword for keyword in call_keywords if keyword.arg ==
                                        "verbose_name" and assert_keyword(keyword)]
                if len(verbose_exist_or_not):
                    print(assign_targets_Name_id, _member.value.func.attr,
                          verbose_exist_or_not[0].value.value)
                    print()
                else:
                    print(assign_targets_Name_id,
                          _member.value.func.attr, "no verbose name")
                    print()


def get_doc__file(file):
    out = dict()
    with open(file, "r") as f:
        p = ast.parse(f.read())
        # get all classes from the given python file.
        classes = [_class for _class in ast.walk(p) if assert_ClassDef(_class)]
        get_doc__class(classes[0])

