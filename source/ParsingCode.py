from pathlib import Path

import jast

from source.AuxJAST import AuxParse


class ParsingCode(jast.JNodeVisitor):
    def __init__(self, file_path: str, file_dir) -> None:
        """Configs for File and Directory"""
        self.mainFile: str = file_path
        self.pathDir = file_dir
        self.name_file: str = self.mainFile[len(self.pathDir) : -5]

        """ Variables for Lines of Code (LOC) """
        self.count_total_lines = 0
        self.count_eff_lines = 0

        """ Coupling Between Objets """
        self.cbo = 0
        self.interacts_of_coupling = []

        """ Variables for Depth of Inheritance and Number of Child """
        self.javafiles = Path(self.pathDir).glob("**/*.java")
        self.depth = 0
        self.names_of_children = []
        self.countChilds = 0

        """ Response for a Class"""
        self.response_for_class_metric = 0

        """ JAVA """
        self.java_classes = []
        self.extends = ""
        self.implements = []
        self.fields = []
        self.methods = []
        self.call_methd = []
        self.objets = []
        self.name_expr = []
        self.types = []

        self.java_objects = []

        """ Calling the 'main' of the parser"""
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
        self.extract_java_classes()

        self.line_of_code()
        self.depth_of_inheritance()
        self.number_of_child(self.name_file, self.pathDir, self.java_classes)
        self.response_for_class()
        self.coupling_btwn_objects()
        self.print_metrics()

    def print_metrics(self):
        print(f"LOC: {self.count_total_lines}")
        print(f"LOC Efficiency: {self.count_eff_lines}")
        print(f"Number of Child: {self.countChilds}")
        print(f"CBO: {self.cbo}")
        print(f"RFC {self.response_for_class()}")

    def extract_java_classes(self):
        for file in self.javafiles:
            if file.name == f"{self.name_file}.java":
                continue
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

        for item in self.java_classes:
            path = f'{item["path"]}{item["class"]}.java'
            aux = AuxParse(path)
            self.java_objects.append(aux)

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

                if stripped_lines[-2:] == "/*":
                    blockComment = False
                    continue

                if stripped_lines[:2] == "//":
                    continue

                if stripped_lines == "{" or stripped_lines == "}":
                    continue

                stripped_lines.rstrip("\n")

                if (
                    stripped_lines or stripped_lines[-1:] == ";"
                ) and blockComment is False:
                    self.count_eff_lines += 1

    def depth_of_inheritance(self):
        return self.depth

    def number_of_child(self, actual_name: str, actual_dir: str, javadict):
        javafiles = javadict

        for sub in javafiles:
            path = f'{sub["path"]}{sub["class"]}.java'

            with open(path) as f:
                lines = f.readlines()

                for line in lines:
                    if "extends " + actual_name in line:
                        self.countChilds += 1
                        javafiles.remove(sub)
                        self.number_of_child(sub["class"], sub["path"], javafiles)
                        break

        return self.countChilds

    def coupling_btwn_objects(self):
        for jclass in self.java_objects:

            for item in self.types:

                if jclass.name_class in item["type"]:
                    self.cbo += 1
                    self.interacts_of_coupling.append(item)

    def lack_of_cohesion_of_methods(self, node):
        pass

    def response_for_class(self):
        """RS = {M} + {Ri}
        - M: set of all methods in the class
        - Ri: set of methods called by the class
        """

        rfc_sum = len(self.methods)
        intersection = []

        for jclass in self.java_objects:
            for method in jclass.methods:
                for ext_method in self.call_methd:
                    if ext_method["func"] in method.id:
                        if {jclass.name_class, method.id} not in intersection:
                            intersection.append({jclass.name_class, method.id})
                            rfc_sum += 1

        self.response_for_class_metric = rfc_sum
        return self.response_for_class_metric

    def weight_methods_class(self):
        """Every method counts at 1"""
        return len(self.methods)

    #
    #   #   jAST AUX METHODS
    #

    #
    # ##    DECLARATIONS
    #

    def visit_Class(self, node: jast.Class):
        if isinstance(node.extends, jast.Class):
            self.extends = self.generic_visit(node.extends)
        for item in node.implements:
            self.visit(item)
        for item in node.body:
            self.visit(item)

    def visit_Method(self, node: jast.Method):
        self.methods.append(node)
        self.visit(node.body)
        self.visit(node.parameters)
        self.visit(node.return_type)

    def visit_Field(self, node: jast.Field):
        self.fields.append(node)
        for item in node.modifiers:
            self.visit(item)
        self.visit(node.type)
        for item in node.declarators:
            self.visit(item)

    def visit_identifier(self, node: jast.identifier):
        return node

    def visit_params(self, node: jast.params):
        for i in node.parameters:
            self.visit(i)

    def visit_param(self, node: jast.param):
        self.visit(node.type)
        self.visit(node.id)
        return node

    def visit_Coit(self, node: jast.Coit):
        """Coit is a 'type' element, we can analyse every 'strange type' that the jAST declare as Coit object on a last node, this used to include all the types of ou Classes declarations."""
        if "lineno" in node.__dict__.keys():
            self.types.append({"type": node.id, "line": node.lineno})
        else:
            self.types.append({"type": node.id})
        if node.type_args != None:
            self.visit(node.type_args)

    def visit_InstanceOf(self, node: jast.InstanceOf):
        pass

    def visit_dim(self, node: jast.dim):
        pass

    #
    # ## Statements
    #

    def visit_LocalVariable(self, node: jast.LocalVariable):
        self.visit(node.type)
        for item in node.declarators:
            self.visit(item)
        return node

    def visit_Assign(self, node: jast.Assign):
        self.visit(node.target)
        self.visit(node.value)

    def visit_This(self, node: jast.This):
        return node

    def visit_LocalType(self, node: jast.LocalType):
        return node

    def visit_If(self, node: jast.If):
        self.visit(node.test)
        self.visit(node.body)
        if node.orelse != None:
            self.visit(node.orelse)

    def visit_Switch(self, node: jast.Switch):
        self.visit(node.value)
        self.visit(node.body)

    def visit_switchblock(self, node: jast.switchblock):
        for item in node.groups:
            self.visit(item)
        for item in node.labels:
            self.visit(item)

    def visit_switchgroup(self, node: jast.switchgroup):
        for item in node.labels:
            self.visit(item)
        for item in node.body:
            self.visit(item)

    def visit_Case(self, node: jast.Case):
        self.visit(node.guard)

    def visit_Expr(self, node: jast.Expr):
        self.visit(node.value)

    def visit_While(self, node: jast.While):
        self.visit(node.body)

    #
    # ## EXPRESSIONS
    #

    def visit_Call(self, node: jast.Call):
        self.visit(node.func)
        for param in node.args:
            self.visit(param)
        self.call_methd.append({"line": node.lineno, "func": node.func.id})

    def visit_declarator(self, node: jast.declarator):
        self.visit(node.id)
        if node.init != None:
            self.visit(node.init)

    def visit_variabledeclaratorid(self, node: jast.variabledeclaratorid):
        return node.id

    def visit_NewObject(self, node: jast.NewObject):
        """Extract the new Object from their line"""

        self.visit(node.type)
        self.objets.append({node.lineno, node.type.id})
        for item in node.args:
            self.visit(item)
        if node.body != None:
            for item in node.body:
                self.visit(item)

    def visit_Name(self, node: jast.Name):
        """Here, we can extract the path of many expressions, and store her position to make a clean parse for the metrics

        Example:
            Client.getStatus()
            * 'Client' and 'getStatus' is a Name object
        """
        self.name_expr.append({"id": node.id, "line": {node.lineno}})

    def visit_BinOp(self, node: jast.BinOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_ArrayType(self, node: jast.ArrayType):
        self.visit(node.type)
        for item in node.dims:
            self.visit(item)

    def visit_arrayinit(self, node: jast.arrayinit):
        for item in node.values:
            self.visit(item)

    def visit_typeargs(self, node: jast.typeargs):
        for item in node.types:
            self.visit(item)

    def visit_Constant(self, node: jast.Constant):
        self.visit(node.value)

    def visit_Member(self, node: jast.Member):
        """jAST, most of the time, classifies functions call with 'member', so we can extract the methods called for RFC, CBO and WMC"""
        self.visit(node.value)
        self.visit(node.member)
        return node
