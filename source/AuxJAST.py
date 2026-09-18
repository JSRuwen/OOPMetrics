import jast


class AuxParse(jast.JNodeVisitor):
    def __init__(self, path_to_file:str) -> None:
        self.file = path_to_file

        """ JAVA """
        self.name_class = ''
        self.java_classes = []
        self.class_dict = {"methods": [], "field": []}
        self.extends = ""
        self.implements = []
        self.body = []
        self.methods = []
        self.call_methd = set()
        self.objets = []
        self.expressions = []

        """ Run Aux Parser"""
        self.run_parser()

    def run_parser(self):
        """
        The main of the code, calls calculate_metrics()
        """
        try:
            with open(self.file) as file:
                tree = jast.parse(file.read())

            self.visit(tree)
        except Exception as e:
            print(f"{self.file} AUX: Houve um erro ao abrir o arquivo:\n{e}")

    def visit_Class(self, node: jast.Class):
        self.name_class = node.id
        if isinstance(node.extends, jast.Class):
            self.extends = self.generic_visit(node.extends)
        for item in node.implements:
            self.visit(item)
        for item in node.body:
            match item.__class__.__name__:
                case "Method":
                    self.class_dict["methods"].append(item)
                    self.methods.append(item)
                case "Field":
                    self.class_dict["field"].append(self.generic_visit(item))

            self.visit(item)
