import jast
import os
import glob

pathDir = "java/simples"
arquivo = "java/simples/helloworld.java"
print("Path existente= " + str(os.path.exists(arquivo)))
# print(os.listdir("."))
# Parse the Java source file
with open(arquivo) as file:
    tree = jast.parse(file.read())


class ParsingCode(jast.JNodeVisitor):
    def __init__(self) -> None:
        self.countADD = 0
        self.fors = 0
        self.ifs = 0
        self.countline = 0
        self.depthinheritance = 0

    def visit_Package(self, node: jast.Package):
        return super().visit_Package(node)

    def visit_Class(self, node: jast.Class):
        print(node.extends)
        # return super().visit_Class(node)

    def visit_Add(self, node: jast.Add):
        return super().visit_Add(node)

    # PRINT DA ÁRVORE #########################################
    def visit_If(self, node):
        self.visit(node.body)
        self.ifs += 1

    def visit_identifier(self, node: jast.identifier):
        print(node)

    def loc(self):
        self.countline = 0
        with open(arquivo, "r") as f:
            # linhas = f.readlines()
            for line in f:
                self.countline += 1
        return self.countline

    # exclui aquelas que possuem apenas delimitadores (p.ex. chaves, parênteses, aspas, begin, end )
    def locEfficiency(self):
        self.countline = 0
        blockComment = False
        with open(arquivo, "r") as f:
            lines = []
            for line in f:  # strip() remove linhas em branco
                lines.append(line.strip())
            for line in lines:
                # print(line[:2])
                if blockComment == True and not (line[-2:] == "*/"):
                    # print("Fechando o bloco")
                    continue
                else:
                    blockComment = False

                if line[:2] == "/*":
                    # print("Encontrou um bloco")
                    blockComment = True
                    continue
                if line[:2] == "//":
                    # print("Encontrou uma linha")
                    continue

                line.rstrip("\n")  # ignora o '\n' na leitura
                if line or line[-1:] == ";":
                    self.countline += 1
        return self.countline

    def depth_of_inheritance(self):
        self.rList = glob.glob("**/*.java", root_dir=pathDir, recursive=True)
        self.countHerancy = 0
        # print(self.rList)
        for arc in self.rList:
            #if arc["extends $1"]:
                # self.countHerancy +=1
            pass

        return len(self.rList)

    def number_of_child(self):
        pass


visitor = ParsingCode()
visitor.visit(tree)
print("LOC: " + str(visitor.loc()))
print("LOC Eficiente: " + str(visitor.locEfficiency()))
print("Depth of Inheritance: " + str(visitor.depth_of_inheritance()))
