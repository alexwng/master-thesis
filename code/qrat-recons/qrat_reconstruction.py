#!/usr/bin/python3

import argparse
import sys
from pysat.formula import CNF
from pysat.solvers import Lingeling

class QratFromQcir:
    def __init__(self):
        self.initVars = -1
        self.tseitinStart = -1
        self.qcirOldVars = {}
        self.tsitinReverse = -1
        self.tseitinOutputClauses = CNF()

    def getInitialVariablesNo(self, filepath):
        file = open(filepath, "r")
        while True:
            line = file.readline()
            if not line:
                break

            if line.startswith("p"):
                self.initVars = int(line.split()[2])

            if not line.startswith("c") and not line.startswith("p") and not line.startswith("a") and not line.startswith("e"):
                foo = line.split()
                disj = []

                for x in foo:
                    if x != "0":
                        bar = int(x)
                        disj.append(bar)

                if len(disj) > 0:
                    self.tseitinOutputClauses.append(disj)
        
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
                disj = []

                for x in foo:
                    if x != "0":
                        bar = int(x)
                        if abs(bar) < self.tseitinStart:
                            literal = str(self.qcirOldVars[bar])
                            disj.append(int(literal))
                        else:
                            if bar < 0:
                                literal = "-" + str(self.tsitinReverse - ((abs(bar)-(self.tseitinStart - 1)) + self.initVars))
                                disj.append(int(literal))
                            else:
                                literal = str(self.tsitinReverse - ((abs(bar)-(self.tseitinStart - 1)) + self.initVars))
                                disj.append(int(literal))

                if len(disj) > 0 and disj[0] != self.initVars + 1:
                    self.tseitinOutputClauses.append(disj)
                    for x in disj:
                        print(str(x) + " ", end="")
                    print(0)

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

    def entaileOutputTseitin(self):
        with Lingeling(bootstrap_with=self.tseitinOutputClauses.clauses, with_proof=True) as l:
            SAT1 = l.solve(assumptions=[-(self.initVars + 1)])
            if SAT1 == False:
                for x in l.get_proof():
                    print(str(self.initVars + 1) + " " + x)
                pass
            else:
                print('Formula is SAT', file=sys.stderr)
                sys.exit(1)
        
        print(str(self.initVars + 1) + " 0")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("initQdimacs")
    parser.add_argument("newQdimacs")
    parser.add_argument("newQrat")
    args = parser.parse_args()
    
    qrat = QratFromQcir()
    qrat.getInitialVariablesNo(args.initQdimacs)
    qrat.getNewQdimacs(args.newQdimacs)
    qrat.entaileOutputTseitin()
    qrat.getQratFromOld(args.newQrat)

main()