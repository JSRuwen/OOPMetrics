import glob
import os
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
        self.extract_java_classes()
        self.depth_of_inheritance()
        self.number_of_child(self.name_file, self.pathDir, self.javafiles)
        self.print_metrics()

    def print_metrics(self):
        print(f"LOC: {self.count_total_lines}")
        print(f"LOC Efficiency: {self.count_eff_lines}")
        print(f'Number of Child: {self.countChilds}')
        print(f"CBO: {self.cbo}")

    def extract_java_classes(self):
        for file in self.javafiles:
            path = self.pathDir
            text = str(file)
            
            if self.pathDir[:2] == "./":
                path = self.pathDir[2:]

            print(file)
            print(path)

            start_idx = text.find(path)
            start_idx += len(path)

            end_idx = text.find(".java", start_idx)

            if start_idx != -1 and end_idx != 1:
                # self.names_of_children.append(
                #     text[start_idx + len(path) : end_idx]
                # )
                print(f'{text[:end_idx]} {text[start_idx:]}')
                javaclassname = text[start_idx: end_idx]
                print(f'{type(javaclassname)}, {type(path)}')
                self.java_classes.append({"class": javaclassname, "path": path})
                print(self.java_classes)

    def line_of_code(self):
        """Return the number of lines, total and effective lines"""

        self.count_total_lines = 0
        self.count_eff_lines = 0
        blockComment = False

        with open(self.mainFile, "r") as f:
            lines = f.readlines()
            self.count_total_lines = len(lines)

            # exclui aquelas que possuem apenas delimitadores (p.ex. chaves, parênteses, aspas, begin, end )
            for line in lines:
                stripped_lines = line.strip()  # strip() remove linhas em branco
                # print(line[:2])
                if blockComment == True and stripped_lines[-2:] != "*/":
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
        return self.depth

    def number_of_child(self, actual_name: str, actual_dir: str, java_files):
        javafiles = java_files
        # print(f"1. {actual_name}")
        child_path = ""

        start_str = actual_dir
        # print(start_str)

        for item in self.java_classes:
            path = f'{item["path"]}{item["class"]}.java'
            with open(path) as f:
                lines = f.readlines()
                for line in lines:
                    print(line)
                    if "extends " + item["class"] in line:
                        self.countChilds += 1
                        javafiles = [x for x in javafiles if x != item]
                        self.number_of_child(item["class"], item["path"], javafiles)
                        break
        return self.countChilds

    def cbo_aux(self, node):
        print(self.java_classes)
        if node in self.java_classes:
            print(f"{node}")
            self.cbo += 1

    #
    #   #   jAST AUX METHODS
    #
    def visit_identifier(self, node: jast.identifier):
        return node

    def visit_Method(self, node: jast.Method):
        body = self.generic_visit(node.body)
        parameters = self.generic_visit(node.parameters)
        self.cbo_aux(body)
        self.cbo_aux(parameters)
        self.cbo_peach_method.append({"method": f"{node.id}", "cbo": self.cbo})
        self.cbo = 0

    # def visit_Class(self, node):
    #     print(node.extends)
