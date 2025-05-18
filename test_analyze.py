#!/usr/bin/env python3

import os
from src.main import analyze

def main():
    print("Starting test analyze")
    analyze(path=os.path.abspath('.'))
    print("Finished test analyze")

if __name__ == "__main__":
    main()
