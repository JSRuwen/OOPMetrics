from source.ParsingCode import ParsingCode

path_to_file: str = "./java/simples/helloworld/helloworld.java"
path_to_dir: str = "./java/simples/helloworld/"


def args_input():
    pass

if __name__ == "__main__":
    app = ParsingCode(path_to_file, path_to_dir)
