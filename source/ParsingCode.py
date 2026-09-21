from pathlib import Path

import jast
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.style import Style
from rich.table import Table

from source.AuxJAST import AuxParse


class ParsingCode(jast.JNodeVisitor):
    def __init__(self, file_path: str, file_dir) -> None:
        """Configs for File and Directory"""
        self.mainFile: str = file_path
        self.pathDir = file_dir
        self.filename: str = self.mainFile[len(self.pathDir) : -5]

        """ Variables for Lines of Code (LOC) """
        self.count_total_lines = 0
        self.count_eff_lines = 0

        """ Coupling Between Objets """
        self.cbo = 0
        self.interacts_of_coupling = []

        """ Variables for Depth of Inheritance and Number of Child """
        self.javafiles = list(Path(self.pathDir).glob("**/*.java"))
        self.depth = 0
        self.names_of_children = []
        self.number_of_child_metric = 0

        """ Response for a Class"""
        self.response_for_class_metric = 0

        """ Lack Cohesion Of Methods """
        self.lCOM_metric = 0

        """ JAVA """
        self.java_classes = []
        self.extends = None
        self.implements = []
        self.constructor = None
        self.fields : set = set()
        self.this : set = set()
        self.assigns : set = set()
        self.methods : set = set()
        self.methods_objects = []
        self.call_methd = []
        self.objets = []
        self.name_expr = []
        self.types = []

        self.java_objects = []
        self.objects_used = []

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
            print(
                "Houve um erro ao abrir o arquivo Principal:"
                + f"\n  {self.mainFile}\n\n{e}"
            )

    #
    #   #   METRICS METHODS
    #

    def calculate_metrics(self):
        """Calculates all the quality metrics for the code"""
        self.extract_java_classes()

        self.line_of_code()
        self.number_of_child(self.filename, self.pathDir, self.java_classes)
        self.depth_of_inheritance(self.extends, self.javafiles)
        self.coupling_btwn_objects()
        self.response_for_class()
        self.lack_of_cohesion_of_methods()
        self.print_metrics()

    def print_metrics(self):
        console = Console()
    
        # Create table
        title: str = f"[bold][#00ffae]{self.filename.upper()}[/]"
        border_style: Style = Style(color="#000000", bold=True,)

        table = Table(title=title,
                      box=box.ROUNDED,
                      show_header=True,
                      header_style="bold #ffee00",
                      border_style=border_style,
                      )


        table.add_column("Complexity", style="cyan")
        table.add_column("Value", justify="right", style="#1cffa0")
        
        table.add_row("Total lines", str(self.count_total_lines))
        table.add_row("Effective lines", str(self.count_eff_lines))
        
        # table.add_row("─" * 20, "─" * 10, style="dim")
        
        # table.add_row("Distinct Operators (n1)", str(self.n1))
        # table.add_row("Distinct Operands (n2)", str(self.n2))
        # table.add_row("Total Operators (N1)", str(self.N1))
        # table.add_row("Total Operands (N2)", str(self.N2))
        # table.add_row("Program vocabulary", str(self.vocabulary))
        # table.add_row("Program Length", str(self.length))
        # table.add_row("Estimated Length", f"{self.estimated_len:.1f}")
        # table.add_row("Volume", f"{self.volume:.1f}")
        # table.add_row("Difficulty", f"{self.difficulty:.1f}")
        # table.add_row("Program estimated level", f"{self.estimated_level:.4f}")
        # table.add_row("Content Intelligence", f"{self.intelligence:.1f}")
        # table.add_row("Effort", f"{self.effort:.1f}")
        # table.add_row("Required time to program", f"{self.time_required:.1f}")
        # table.add_row("Delivered bugs", f"{self.delivered_bugs:.1f}")
        
        # Adicionar separador para a complexidade ciclomática
        table.add_row("─" * 20, "─" * 10, style="dim")
        table.add_row("[bold]C&K: Chidamber and Kemerer[/]", "")
        table.add_row("Number of Child", str(self.number_of_child_metric))
        table.add_row("Depth of Inheritance", str(self.depth))
        table.add_row("Coupling Between Objects", str(self.cbo))
        table.add_row("Response for Class", str(self.response_for_class_metric))
        table.add_row("Lack Cohesion of Methods", f"{self.lCOM_metric:.2f}")
        table.add_row("Weight Method Class", f"{self.weight_methods_class()}")




        table.add_row("─" * 20, "─" * 10, style="dim")
        # table.add_row("[bold]OTHERS[/]", "")
        # table.add_row("Average line volume", str(round(self.avg_line_volume)))
        #
        # table.add_row("Number of functions calls", str(self.total_func_calls))

        # Imprimir a tabela
        console.print(table)

    def extract_java_classes(self):
        if self.extends != None:
            for file in self.javafiles:
                if f'{self.extends}.java' == file.name:
                    parent = AuxParse(str(file))

                    fields = {x.strip() for x in self.fields} | {x.strip() for x in parent.fields}
                    self.fields = fields
                    
                    methods = {x.strip() for x in self.methods} | {x.strip() for x in parent.methods}
                    self.methods = methods
                    break

        for file in self.javafiles:
            if file.name == f"{self.filename}.java":
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

                if stripped_lines[-2:] == "*/":
                    blockComment = False
                    continue

                if stripped_lines[:2] == "//":
                    continue

                if stripped_lines == "{" or stripped_lines == "}":
                    continue

                stripped_lines.rstrip("%n")
                stripped_lines.rstrip("\n")

                if (
                    stripped_lines or stripped_lines[-1:] == ";"
                ) and blockComment is False:
                    self.count_eff_lines += 1

    def depth_of_inheritance(self, jclass, jfiles : list):
        if jclass != None:
            for file in jfiles:
                if jclass == file.name[:-5]:
                    aux = AuxParse(file)
                    self.depth_of_inheritance(aux.extends, jfiles)
                    self.depth += 1
            
        return self.depth

    def number_of_child(self, actual_name: str, actual_dir: str, javadict):
        javafiles = javadict

        for sub in javafiles:
            path = f'{sub["path"]}{sub["class"]}.java'

            with open(path) as f:
                lines = f.readlines()

                for line in lines:
                    if "extends " + actual_name in line:
                        self.number_of_child_metric += 1
                        break

        return self.number_of_child_metric

    def coupling_btwn_objects(self):
        self.cbo = 0
        types_set = set()
        for jclass in self.java_objects:

            for item in self.types:
                if jclass.filename in item["type"]:
                    if item["type"].strip() not in {x.strip() for x in types_set}:
                        self.cbo += 1
                        types_set.add(item["type"])
                    self.objects_used.append(jclass)


    def lack_of_cohesion_of_methods(self):
        count = 0

        if self.fields == set():
            return
        
        if self.constructor != None:
            cons_fields = [x for x in self.name_expr if self.constructor.lineno < x["line"] < self.constructor.end_lineno]

            for field in self.fields:

                for item in cons_fields:
                    # print(f'{field} in {item}')
                    ext = {field.strip()} & {item["id"].strip()}
                    if ext != set():
                        count += 1
                        break

        for field in self.fields:
            
            for method in self.methods_objects:

                fields = [x for x in self.name_expr if method.lineno <x["line"] < method.end_lineno]
                for item in fields:
                    ext = {field.strip()} & {item["id"].strip()}
                    if ext != set():
                        count += 1
                        break

        calc = None
        
        try:
            # print(f'1 - {count} / {len(self.methods)} * {len(self.fields)}')
            calc = 1 - (count / (len(self.methods) * len(self.fields)))
        except ZeroDivisionError as e:
            pass
        finally:
            self.lCOM_metric = calc


    def response_for_class(self):
        """RS = {M} + {Ri}
        - M: set of all methods in the class
        - Ri: set of methods called by the class
        """

        rfc_sum = len(self.methods)
        intersection = []

        for jclass in self.objects_used:
            for method in jclass.methods:
                for ext_method in self.call_methd:
                    if ext_method["func"] in method:
                        result = {jclass.filename, method} 
                        if result not in intersection:
                            intersection.append({jclass.filename, method})
                            rfc_sum += 1
                            break

        self.response_for_class_metric = rfc_sum + 1
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
        if isinstance(node.extends, jast.jtype):
            self.extends = self.generic_visit(node.extends)
        for item in node.implements:
            self.visit(item)
        for item in node.body:
            self.visit(item)

    def visit_Method(self, node: jast.Method):
        self.methods.add(node.id)
        self.methods_objects.append(node)
        self.visit(node.body)
        self.visit(node.parameters)
        self.visit(node.return_type)

    def visit_Block(self, node: jast.Block):
        for item in node.body:
            self.visit(item)

    def visit_Constructor(self, node: jast.Constructor):
        for item in node.modifiers:
            self.visit(item)
        self.constructor = node
        self.visit(node.id)
        self.visit(node.parameters)
        self.visit(node.body)

    def visit_Field(self, node: jast.Field):
        for item in node.modifiers:
            self.visit(item)
        self.visit(node.type)
        for item in node.declarators:
            self.visit(item)
            self.fields.add(item.id.id)

    def visit_Return(self, node: jast.Return):
        if node.value != None:
            self.visit(node.value)

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
        self.assigns.add(node.target)
        self.visit(node.target)
        self.visit(node.value)

    def visit_This(self, node: jast.This):
        self.this.add(node.lineno)
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

    def visit_Try(self, node: jast.Try):
        self.visit(node.body)
        for item in node.catches:
            self.visit(item)
        if node.final != None:
            self.visit(node.final)

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
        self.name_expr.append({"id": node.id, "line": node.lineno})

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
