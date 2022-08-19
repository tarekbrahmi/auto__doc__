import ast

# members = [attr for attr in dir(example) if not callable(getattr(example, attr)) and not attr.startswith("__")]

def get_doc(file):

    out = dict()
    with open(file, "r") as f:
        p = ast.parse(f.read())
        # get all classes from the given python file.
        classes = [c for c in ast.walk(p) if isinstance(c, ast.ClassDef)]

        for x in classes:
            out[x.name] = [fun.name for fun in ast.walk(
                x) if isinstance(fun, ast.FunctionDef)]

    return out
get_doc(__file__)