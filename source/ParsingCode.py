from pathlib import Path

import jast


class ParsingCode(jast.JNodeVisitor):
    def __init__(self, file_path: str, file_dir) -> None:
        """Configs for File and Directory"""
        self.mainFile: str = file_path
        self.pathDir = file_dir
        self.name_file: str = self.mainFile[len(self.pathDir) : -5]

        self.countADD = 0
        self.fors = 0
        self.ifs = 0

        """ Variables for Lines of Code (LOC) """
        self.count_total_lines = 0
        self.count_eff_lines = 0

        """ Variables for Depth of Inheritance and Number of Child """
        self.javafiles = Path(self.pathDir).glob("**/*.java")
        self.depth = 0
        self.names_of_children = []
        self.countChilds = 0

        """ CBO """
        self.java_classes = []
        self.cbo = 0
        self.cbo_peach_method = []
        self.methods = []

        """ Calling the 'main' of the parser"""
        self.extract_java_classes()
        self.run_parser()

    #
    #   #   METHODS
    #

    def run_parser(self):
        """
        The main of the code, calls calculate_metrics()
        """
        try:
            with open(self.mainFile) as file:
                tree = jast.parse(file.read())

            self.visit(tree)
            self.calculate_metrics()
        except Exception as e:
            print(f"{self.mainFile} Houve um erro ao abrir o arquivo:\n{e}")

    #
    #   #   METRICS METHODS
    #

    def calculate_metrics(self):
        """Calculates all the quality metrics for the code"""

        self.line_of_code()
        self.depth_of_inheritance()
        self.number_of_child(self.name_file, self.pathDir, self.java_classes)
        self.print_metrics()

    def print_metrics(self):
        print(f"LOC: {self.count_total_lines}")
        print(f"LOC Efficiency: {self.count_eff_lines}")
        print(f"Number of Child: {self.countChilds}")
        print(f"CBO: {self.cbo_peach_method}")
        print(f"{self.methods}")

    def extract_java_classes(self):
        for file in self.javafiles:
            path = self.pathDir
            text = str(file)

            if self.pathDir[:2] == "./":
                path = self.pathDir[2:]

            start_idx = text.find(path)
            start_idx += len(path)

            end_idx = text.find(".java", start_idx)

            if start_idx != -1 and end_idx != 1:
                javaclassname = text[start_idx:end_idx]
                self.java_classes.append({"class": javaclassname, "path": path})

    def line_of_code(self):
        """Return the number of lines, total and effective lines"""

        self.count_total_lines = 0
        self.count_eff_lines = 0

        with open(self.mainFile, "r") as f:
            lines = f.readlines()
            self.count_total_lines = len(lines)

            blockComment = False

            for line in lines:
                stripped_lines = line.strip()

                if stripped_lines[:2] == "/*":
                    blockComment = True
                    continue

                if stripped_lines[-2:] == "*/":
                    blockComment = False
                    continue

                if stripped_lines[:2] == "//":
                    continue

                if stripped_lines == "{" or stripped_lines == "}":
                    continue

                stripped_lines.rstrip("\n")

                if (stripped_lines or stripped_lines[-1:] == ";") and blockComment is False:
                    print(line)
                    self.count_eff_lines += 1

    def depth_of_inheritance(self):
        return self.depth

    def number_of_child(self, actual_name: str, actual_dir: str, javadict):
        javafiles = javadict
        for item in self.java_classes:
            for sub in self.java_classes:
                path = f'{sub["path"]}{sub["class"]}.java'
                with open(path) as f:
                    lines = f.readlines()
                    for line in lines:
                        if "extends " + item["class"] in line:
                            self.countChilds += 1
                            javafiles.remove(item)
                            self.number_of_child(sub["class"], sub["path"], javafiles)
                            break
        return self.countChilds

    def method_scan(self, node):
        print(f"method. {node.__dict__}")
        print(f"  params. {node.parameters.__dict__}")
        print(f"  body. {node.body.__dict__}")

        param = []
        for item in node.parameters.__dict__["parameters"]:
            param.append(
                {
                    "type": self.generic_visit(item.type),
                    "id": self.generic_visit(item.id),
                }
            )
        print(f"param_format: {param}")

        body = []
        print(f'    body dict: {node.body.__dict__["body"]}')
        for item in node.body.__dict__["body"]:
            match item.__class__.__name__:
                case "LocalVariable":
                    body_aux = {
                        f"{item.__class__.__name__}": f"line {item.lineno}",
                        "type": item.type.__class__.__name__,
                        "decl": [],
                    }
                    if body_aux["type"] == "Coit":
                        body_aux["type"] = self.generic_visit(item.type)

                    for i in item.declarators:
                        body_aux["decl"].append(
                            {
                                "id": self.generic_visit(i.id),
                                "init": self.generic_visit(i.init),
                            }
                        )
                    body.append(body_aux)
                case "Expr":
                    body_aux = {
                        f"{item.__class__.__name__}": f"line {item.lineno}",
                        "args": [],
                    }
                    if "Member" in item.__dict__["value"].__class__.__name__:
                        body_aux["member"] = self.generic_visit(item.value.member)

                    if "Call" in item.__dict__["value"].__class__.__name__:
                        body_aux["func"] = self.generic_visit(item.value.func)
                    body.append(body_aux)
        method = {
            "id": node.__dict__["id"],
            "parameters": param,
            "body": body,
            "return": node.return_type.__class__.__name__,
        }
        self.methods.append(method)

    def cbo_metric():
        pass

    def lcom_aux(self, node):
        pass

    def response_for_class_metric(self):
        """RS = {M} + {Ri}
        M: set of all methods in the class
        Ri: set of methods called by the class
        """
        rfc_sum = len(self.methods)
        return rfc_sum

    #
    #   #   jAST AUX METHODS
    #
    def visit_identifier(self, node: jast.identifier):
        # print(f"visit id: {node}")
        return node

    def visit_Method(self, node: jast.Method):
        self.method_scan(node)

    def visit_params(self, node: jast.params):
        print(f"   params: {node.__dict__}")
        for i in range(0, len(node.__dict__["parameters"]), 1):
            self.visit(node.__dict__["parameters"][i])

    def visit_param(self, node: jast.param):
        print(f"    param: {node.__dict__}")
        self.visit(node.type)
        self.visit(node.id)
        return node

    def visit_Coit(self, node: jast.Coit):
        print(f"coit: {node.__dict__}")
        return node

    def visit_Expr(self, node: jast.Expr):
        print(f"     Expr: {node.__dict__}")
        self.visit(node.value)

    def visit_Call(self, node: jast.Call):
        print(f"call: {node.__dict__}")
        print(node.__dict__["func"].__dict__)

    def visit_Constant(self, node: jast.Constant):
        print(node.value)

    def visit_InstanceOf(self, node: jast.InstanceOf):
        print(f" Inst Of: {node.__dict__}")

    def visit_variabledeclaratorid(self, node: jast.variabledeclaratorid):
        print(f"vardecid: {node.__dict__}")
        return node.id

    def visit_dim(self, node: jast.dim):
        print(f"dim: {node.__dict__}")

    def visit_LocalVariable(self, node: jast.LocalVariable):
        print(f"    var local: {node.__dict__}")

    def visit_declarator(self, node: jast.declarator):
        return node

    def visit_Name(self, node: jast.Name):
        return node

    def visit_Member(self, node: jast.Member):
        return node
