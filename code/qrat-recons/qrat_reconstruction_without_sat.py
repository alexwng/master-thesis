#!/usr/bin/python3

import argparse

class QratFromQcir:
    def __init__(self):
        self.initVars = -1
        self.tseitinStart = -1
        self.qcirOldVars = {}
        self.tsitinReverse = -1

    def getInitialVariablesNo(self, filepath):
        file = open(filepath, "r")
        while True:
            line = file.readline()
            if not line:
                break

            if line.startswith("p"):
                self.initVars = int(line.split()[2])
                break
        
        file.close()

    def getNewQdimacs(self, filepath):
        file = open(filepath, "r")
        totalVarsQcir = 0
        while True:
            line = file.readline()
            if not line:
                break
            
            if line.startswith("c"):
                if "VarOld" in line:
                    foo = line.split()
                    self.qcirOldVars[int(foo[2])] = int(foo[4])
                    self.qcirOldVars[-int(foo[2])] = -int(foo[4])

                if "TseitinStart" in line:
                    self.tseitinStart = int(line.split()[2])

            if line.startswith("p"):
                totalVarsQcir = int(line.split()[2])
                self.tsitinReverse = (self.initVars + 1) + (self.initVars + totalVarsQcir - self.tseitinStart + 1)

            # Add Tseitin to output
            if not line.startswith("c") and not line.startswith("p") and not line.startswith("a") and not line.startswith("e"):
                foo = line.split()

                for x in foo:
                    if x == "0":
                        print(x)
                    else:
                        bar = int(x)
                        if abs(bar) < self.tseitinStart:
                            print(str(self.qcirOldVars[bar]) + " ", end="")
                        else:
                            if bar < 0:
                                print("-" + str(self.tsitinReverse - ((abs(bar)-(self.tseitinStart - 1)) + self.initVars)) + " ", end="")
                            else:
                                print(str(self.tsitinReverse - ((abs(bar)-(self.tseitinStart - 1)) + self.initVars)) + " ", end="")

        file.close()

    def getQratFromOld(self, filepath):
        file = open(filepath, "r")
        while True:
            line = file.readline()
            if not line:
                break

            foo = line.split()

            for x in foo:
                if x == "u" or x == "d":
                    print(x + " ", end="")
                elif x == "0":
                    print(x)
                else:
                    bar = int(x)
                    if abs(bar) < self.tseitinStart:
                        print(str(self.qcirOldVars[bar]) + " ", end="")
                    else:
                        if bar < 0:
                            print("-" + str(self.tsitinReverse - ((abs(bar)-(self.tseitinStart - 1)) + self.initVars)) + " ", end="")
                        else:
                            print(str(self.tsitinReverse - ((abs(bar)-(self.tseitinStart - 1)) + self.initVars)) + " ", end="")
                        
        file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("initQdimacs")
    parser.add_argument("newQdimacs")
    parser.add_argument("newQrat")
    args = parser.parse_args()
    
    qrat = QratFromQcir()
    qrat.getInitialVariablesNo(args.initQdimacs)
    qrat.getNewQdimacs(args.newQdimacs)
    qrat.getQratFromOld(args.newQrat)

main()