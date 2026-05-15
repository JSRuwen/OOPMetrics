import jast
from pathlib import Path
import os
import glob

pathDir = "java/simples"

if pathDir[-1:] != "/": pathDir += "/"
mainFile = "java/simples/helloworld2.java"
name_file = mainFile[len(pathDir):-5]
print(name_file)
print("Path existente= " + str(os.path.exists(mainFile)))
# print(os.listdir("."))
# Parse the Java source file
with open(mainFile) as file:
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

    def line_of_code(self):
        self.totalline = 0
        self.count_eff_lines = 0
        blockComment = False

        with open(mainFile, "r") as f:
            lines = f.readlines()
            self.totalline = len(lines)
            
            # exclui aquelas que possuem apenas delimitadores (p.ex. chaves, parênteses, aspas, begin, end )
            for line in lines:
                stripped_lines = line.strip()# strip() remove linhas em branco
                # print(line[:2])
                if blockComment == True and not (stripped_lines[-2:] == "*/"):
                    # print("Fechando o bloco")
                    continue
                else:
                    blockComment = False
                if "/*" in stripped_lines or "*/" in stripped_lines:
                    continue
                if stripped_lines[:2] == "/*":
                    blockComment = True
                    continue
                if stripped_lines[:2] == "//":
                    continue
                if stripped_lines == "{" or stripped_lines == "}":
                    continue
                stripped_lines.rstrip("\n")  # ignora o '\n' na leitura
                if stripped_lines or stripped_lines[-1:] == ";":
                    self.count_eff_lines += 1

    def depth_of_inheritance(self):
        self.javafiles = Path(pathDir).glob("**/*.java")
        self.depth = 0
        # print(self.rList)
        # for file in self.javafiles:
        #     with open(file) as f:
        #         for line in f:
        #             # Read only the first line
        #             if "extends " + name_file in line:
        #                 self.depth += 1
        #                 break
        #             break
        #

        return self.depth

    def number_of_child(self):
        self.javafiles = Path(pathDir).glob("**/*.java")
        self.countChilds = 0
        # print(self.rList)
        for file in self.javafiles:
            with open(file) as f:
                for line in f:
                    # Read only the first line
                    if "extends " + name_file in line:
                        self.countChilds += 1
                        break
                    break

        return self.countChilds
        pass

def call_main():
    visitor = ParsingCode()
    visitor.visit(tree)
    print("LOC: " + str(visitor.line_of_code()))
    print("Depth of Inheritance: " + str(visitor.depth_of_inheritance()))
    print(str(visitor.number_of_child()))
