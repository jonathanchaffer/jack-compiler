from jackyacc import main as compile
import sys
import os

def main(path):
    if path.endswith('.jack'):
        compile(path)
    else:
        for filename in os.listdir(path):
            if filename.endswith('.jack'):
                if not path.endswith('/'):
                    path = path + '/'
                compile(path + filename)

if __name__ == '__main__':
    main(sys.argv[1])
