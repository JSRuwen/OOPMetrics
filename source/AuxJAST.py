import jast


class AuxParse(jast.JNodeVisitor):
    def __init__(self, path_to_file:str) -> None:
        self.file = path_to_file

        """ JAVA """
        self.filename = ''
        self.java_classes = []
        self.extends = None
        self.implements = []
        self.body = []
        self.methods = set()
        self.fields = set()
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
            print(f"Houve um erro ao abrir o arquivo Secundário: {self.file}\n\n{e}")

    def visit_Class(self, node: jast.Class):
        self.filename = node.id
        if isinstance(node.extends, jast.Class):
            self.extends = self.generic_visit(node.extends)
        for item in node.implements:
            self.visit(item)
        for item in node.body:
            self.visit(item)

    def visit_Method(self, node: jast.Method):
        self.methods.add(node.id)
        self.visit(node.body)
        self.visit(node.parameters)
        self.visit(node.return_type)

    def visit_Field(self, node: jast.Field):
        for item in node.modifiers:
            self.visit(item)
        self.visit(node.type)
        for item in node.declarators:
            self.visit(item)
            self.fields.add(item.id.id)
