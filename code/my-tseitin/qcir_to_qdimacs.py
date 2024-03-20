#!/usr/bin/python3

import sys
import logging
from enum import Enum
import argparse

class QunatifierType(Enum):
    FORALL = 1
    EXISTS = 2

class GateType(Enum):
    AND = 1
    OR = 2

class Qunatifier:
    def __init__(self, qunatifierType, vars):
        self.qunatifierType = qunatifierType
        self.vars = vars

class Gate:
    def __init__(self, id, gateType, vars):
        self.id = id
        self.gateType = gateType
        self.vars = vars

class QCIR:
    def __init__(self):
        self.quantifiers = []
        self.gates = []
        self.outputGateId = -1
        self.gateQdimacsBefore = {} # gate : qdimacs

    def parse(self, filepath):
        # if(filepath == 'stdin'):
        #     file = sys.stdin
        # else:
        file = open(filepath, "r")

        while True:
            line = file.readline()
            if not line:
                break
            
            if(line.startswith("#VarName")):
                foo = line.replace('#VarName', '').replace(' ', '').replace('\n', '').split(':')
                self.gateQdimacsBefore[foo[0]] = foo[1][1:]
                continue

            if(line.lower().startswith("forall")):
                varsList = line[line.find('(') + 1 : line.find(')')].replace(' ','').split(',')
                self.quantifiers.append(Qunatifier(QunatifierType.FORALL, varsList))
                continue
            if(line.lower().startswith("exists")):
                varsList = line[line.find('(') + 1 : line.find(')')].replace(' ','').split(',')
                self.quantifiers.append(Qunatifier(QunatifierType.EXISTS, varsList))
                continue
            if(line.lower().startswith("output")):
                varsList = line[line.find('(') + 1 : line.find(')')].replace(' ','').split(',')
                self.outputGateId = varsList[0]
                continue
            
            
            if '=' in line:
                if "and" in line.lower():
                    foo = line.lower().replace(' ', '').split('=')
                    gateId, varsList = foo[0], foo[1][foo[1].find('(') + 1:foo[1].find(')')].split(',')
                    self.gates.append(Gate(gateId, GateType.AND, varsList))
                elif "or" in line.lower():
                    foo = line.lower().replace(' ', '').split('=')
                    gateId, varsList = foo[0], foo[1][foo[1].find('(') + 1:foo[1].find(')')].split(',')
                    self.gates.append(Gate(gateId, GateType.OR, varsList))

        file.close()

def varNegation(var):
    if var[0] == '-':
        return var[1:]
    else:
        return '-' + var

def varAbs(var):
    if var[0] == '-':
        return var[1:]
    else:
        return var

class QCIRtoQDIMACS:
    def __init__(self):
        self.tseitinPosition = 0
        self.varPosition = 0
        self.gateToTseitin = {}
        self.cnf = []
        self.vars = {}
        self.varTseitinStart = 0

    def getCNF(self, qcir):
        for gate in qcir.gates:
            if gate.gateType == GateType.AND:

                if len(gate.vars) == 1:
                    A = gate.vars[0]
                    if A in self.gateToTseitin:
                        A = self.gateToTseitin[A]
                    
                    self.tseitinPosition += 1
                    C = "t" + str(self.tseitinPosition)

                    self.cnf.append([C, varNegation(A)])
                    self.cnf.append([varNegation(C), A])

                    self.gateToTseitin[gate.id] = C
                    self.gateToTseitin[varNegation(gate.id)] = varNegation(C)
                    continue

                self.tseitinPosition += 1
                A = gate.vars[0]
                B = gate.vars[1]
                C = "t" + str(self.tseitinPosition)
                if A in self.gateToTseitin:
                    A = self.gateToTseitin[A]

                if B in self.gateToTseitin:
                    B = self.gateToTseitin[B]

                self.cnf.append([varNegation(A), varNegation(B), C])
                self.cnf.append([varNegation(C), A])
                self.cnf.append([varNegation(C), B])
                A = C

                for i in range(2, len(gate.vars)):
                    B = gate.vars[i]
                    if B in self.gateToTseitin:
                        B = self.gateToTseitin[B]

                    self.tseitinPosition += 1
                    C = "t" + str(self.tseitinPosition)

                    self.cnf.append([varNegation(A), varNegation(B), C])
                    self.cnf.append([varNegation(C), A])
                    self.cnf.append([varNegation(C), B])

                    A = C
                
                self.gateToTseitin[gate.id] = C
                self.gateToTseitin[varNegation(gate.id)] = varNegation(C)


            if gate.gateType == GateType.OR:
                
                if len(gate.vars) == 1:
                    A = gate.vars[0]
                    if A in self.gateToTseitin:
                        A = self.gateToTseitin[A]
                    
                    self.tseitinPosition += 1
                    C = "t" + str(self.tseitinPosition)

                    self.cnf.append([C, varNegation(A)])
                    self.cnf.append([varNegation(C), A])

                    self.gateToTseitin[gate.id] = C
                    self.gateToTseitin[varNegation(gate.id)] = varNegation(C)
                    continue

                self.tseitinPosition += 1
                A = gate.vars[0]
                B = gate.vars[1]
                C = "t" + str(self.tseitinPosition)
                if A in self.gateToTseitin:
                    A = self.gateToTseitin[A]

                if B in self.gateToTseitin:
                    B = self.gateToTseitin[B]

                self.cnf.append([A, B, varNegation(C)])
                self.cnf.append([C, varNegation(A)])
                self.cnf.append([C, varNegation(B)])
                A = C

                for i in range(2, len(gate.vars)):
                    B = gate.vars[i]
                    if B in self.gateToTseitin:
                        B = self.gateToTseitin[B]

                    self.tseitinPosition += 1
                    C = "t" + str(self.tseitinPosition)

                    self.cnf.append([A, B, varNegation(C)])
                    self.cnf.append([C, varNegation(A)])
                    self.cnf.append([C, varNegation(B)])

                    A = C
                
                self.gateToTseitin[gate.id] = C
                self.gateToTseitin[varNegation(gate.id)] = varNegation(C)

    def CNFvars(self):
        for disj in self.cnf:
            for i in range(len(disj)):
                if varAbs(disj[i])[0] == 't':
                    continue

                if disj[i] in self.vars:
                    disj[i] = self.vars[disj[i]]
                else:
                    self.varPosition += 1
                    self.vars[varAbs(disj[i])] = self.varPosition
                    self.vars[varNegation(varAbs(disj[i]))] = -self.varPosition
                    disj[i] = self.vars[disj[i]]

    def CNFtseitin(self):
        self.varTseitinStart = self.varPosition + 1

        for disj in self.cnf:
            for i in range(len(disj)):
                if type(disj[i]) == int:
                    continue

                if disj[i] in self.vars:
                    disj[i] = self.vars[disj[i]]
                else:
                    self.varPosition += 1
                    self.vars[varAbs(disj[i])] = self.varPosition
                    self.vars[varNegation(varAbs(disj[i]))] = -self.varPosition
                    disj[i] = self.vars[disj[i]]

            disj.sort(key=abs)

    def addQunatifierTseitinAndAdjust(self, qcir):
        for quant in qcir.quantifiers:
            for i in range(len(quant.vars)):
                quant.vars[i] = self.vars[quant.vars[i]]
            quant.vars.sort(key=abs)
        
        if len(qcir.quantifiers) == 0 or qcir.quantifiers[-1].qunatifierType == QunatifierType.FORALL:
            qcir.quantifiers.append(Qunatifier(QunatifierType.EXISTS, range(self.varTseitinStart, self.varPosition + 1)))
        else:
            for x in range(self.varTseitinStart, self.varPosition + 1):
                qcir.quantifiers[-1].vars.append(x)

    def getQDIMACS(self, qcir):
        self.getCNF(qcir)
        self.CNFvars()
        self.CNFtseitin()

        if self.varTseitinStart <= self.varPosition:
            self.addQunatifierTseitinAndAdjust(qcir)

        for oldVar in qcir.gateQdimacsBefore.keys():
            print("c VarOld " + str(self.vars[oldVar]) + " : " + qcir.gateQdimacsBefore[oldVar])
        print("c TseitinStart " + str(self.varTseitinStart))
        print("p cnf " + str(self.varPosition) + " " + str(len(self.cnf) + 1)) # Adding the output

        for quant in qcir.quantifiers:
            if quant.qunatifierType == QunatifierType.FORALL:
                print("a ", end="")
            elif quant.qunatifierType == QunatifierType.EXISTS:
                print("e ", end="")
            for x in quant.vars:
                print(str(x) + " ", end="")
            print(0)

        for disj in self.cnf:
            for x in disj:
                print(str(x) + " ", end="")
            print(0)
        
        if qcir.outputGateId in self.gateToTseitin:
            print(str(self.vars[self.gateToTseitin[qcir.outputGateId]]) + " 0")
        else:
            print(str(self.vars[qcir.outputGateId]) + " 0")

def main():
    logging.getLogger().setLevel(logging.INFO)
    logging.disable()

    parser = argparse.ArgumentParser()
    parser.add_argument("qcirInput")
    args = parser.parse_args()

    qcir = QCIR()
    qcir.parse(args.qcirInput)
    qdimacs = QCIRtoQDIMACS()
    qdimacs.getQDIMACS(qcir)

main()