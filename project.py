"""Transforming MathML files into executable functions in Python"""

# Authur: Peishi JIANG

from libsbml import *
import rdflib
import suc
import operator as op
import re
from math import *
from os import listdir
from pprint import pprint
import itertools
import quantities as pq
import numpy as np
from numerical import findRoot

method = findRoot()

def outputExplicitDirect(tpara, tvar, tfunc, standardunit, symball):
    '''
    Generate the output of the target equation (explicit) based on
    the given inputs
    '''
    paracashe = []
    for ele in tpara:
        inputs = raw_input('Enter the value of ' + ele + \
                           ' with a unit if not dimensionless:')
        paracashe.append(semanticUnitConvert(inputs,standardunit[symall.index(ele)]))
    tinput = ','.join(paracashe)
    output = eval('tfunc(' + tinput +')')
    #print str(tvar[0]) + ': ' + output + ' ' + standardunit[symall.index(tvar[0])]
    return [output, paracashe]

def outputImplicitDirect(tpara, tvar, teqn, standardunit, symall):
    '''
    Enter the inputs of the target eqnuation (implicit);
    conduct the unit conversion; and transform it into an python function 
    '''
    paracashe = []
    for ele in tpara:
        inputs = raw_input('Enter the value of ' + ele + \
                           ' with a unit if not dimensionless:')
        paracashe.append(semanticUnitConvert(inputs,standardunit[symall.index(ele)]))
    global func1
    #print 'lambda '+ ','.join(tpara+tvar) + ':' + teqn
    func1 = eval('lambda '+ ','.join(tpara+tvar) + ':' + teqn)
    tinput = ','.join(paracashe)
    functarget = eval('lambda '+ ','.join(tvar) + ':' + 'func1(' + \
                 tinput + ',' + ','.join(tvar) + ')')
    output = str(method.NewtonRaphson(functarget))
    #print str(tvar[0]) + ': ' + output + ' ' + standardunit[symall.index(tvar[0])]
    return [output, paracashe]

def semanticUnitConvert(unit1v,unit2):
    '''
    Semantically convert the units of input to the standard units parsed
    from the semantic contents of the symbols and return the coefficient of it
    Note: by calling 'semanticUnitConvert'
    '''
    # split the value & units
    unit1v = unit1v.replace(' ','')
    form = re.compile('[0-9.]+')
    value = form.match(unit1v).group()
    unit1 = unit1v.replace(value,'')
    unit1 = unit1.lower(); unit2 = unit2.lower()
    # judge whether unit is the same as standard unit
    # if not, convert it
    if unit1 != unit2:
        form1 = re.compile('[a-zA-Z]+')
        unit1set = form1.findall(unit1)
        unit2set = form1.findall(unit2)
        coefficient = []
        # conversion part
        for i in range(len(unit1set)):
            coef = suc.semanticUnitConversion(unit1set[i],unit2set[i])
            unit1 = unit1.replace(unit1set[i],str(coef),1)
        #print unit1
        return str(eval(value + '*' +unit1))
    else:
        return value

def unitConvert(inputs,standard):
    '''
    Convert the units of input to the standard units parsed from the
    semantic contents of the symbols and return the coefficient of it
    '''
    # check whether dimensionless
    if standard == '':
        return inputs
    # split the value & units
    inputs = inputs.replace(' ','')
    form = re.compile('[0-9.]+')
    value = form.match(inputs).group()
    unit = inputs.replace(value,'')
    # judge whether unit is the same as standard unit
    # if not, convert it
    if unit == standard:
        return value
    else:
        form1 = re.compile('[a-zA-Z]+')
        unit1 = form1.findall(unit)
        unit2 = form1.findall(standard)
        coefficient = []
        # conversion part
        for i in range(len(unit1)):
            exec('coef = 1*pq.' + unit1[i])
            exec('coef.units = pq.' + unit2[i])
            coef = form.match(str(coef)).group()
            unit = unit.replace(unit1[i],coef,1)
        return str(eval(value + '*' +unit))
        
class MathMLConvert:
    '''
    Convert an equation to MathML file(.xml).
    Convert MathML file(.xml) to python function.
    '''

    def __init__(self):
        self.mathmlString = ''
        self.mathString = ''
        self.eqnType = 0
        self.sym = []

    def MathMLToFunction(self,locmathml):
        '''
        Convert MathML to a function callable by python
        '''
        # read MathML from the XML file
        self.mathmlString=open(locmathml).readlines()
        # convert MathML to a mathematical expression in string
        self.mathString = self.MathMLToEqn(self.mathmlString)
        # parse MathML to an executable function
        if re.match('lambda',self.mathString):
            self.eqnType = 1
            self.sym = self.FindSymbol(self.mathmlString,self.eqnType)
            [self.eqnF,self.mathString] = self.TransformFuncLambda(self.mathString)
        else:
            self.eqnType = 2
            self.sym = self.FindSymbol(self.mathmlString,self.eqnType)
            self.eqnF = eval(self.TransformFuncNoLambda(self.mathString,self.sym))
        return [self.sym, self.eqnF, self.mathString]
    
    def EqnToMathML(self,Eqn):
        '''
        Convert equations/functions to MathML expression in string
        '''
        mathml = parseFormula(Eqn)
        self.mathmlString = writeMathMLToString(mathml)
        return self.mathmlString

    def MathMLToEqn(self,mathmlString):
        '''
        Convert MathML to equations/functions
        '''
        xml=''.join(mathmlString)
        ast = readMathMLFromString(xml)
        self.mathString = formulaToString(ast)
        return self.mathString

    def FindSymbol(self,mathmlString,eqnType):
        '''
        find symbols in a MathML form. If it is a lambda function,
        variables are defined in <bvar> (Type = 1). If it is not, variables
        are defined in <ci> (Type = 2).
        '''
        form = re.compile('<ci>[\s]*[\w]*[\s]*</ci>')
        if eqnType == 1: # a lamda function
            for ele in mathmlString:
                if '<bvar>' in ele:
                    cashe = form.search(ele).group()[4:-5]
                    cashe = cashe.replace(' ','')
                    self.sym.append(cashe)
        elif eqnType == 2: # w/o lambda function
            for ele in mathmlString:
                if '<ci>' in ele:
                    cashe = form.search(ele).group()[4:-5]
                    cashe = cashe.replace(' ','')
                    if cashe not in self.sym: self.sym.append(cashe)
        else:
            print 'Type in a wrong number'
        return self.sym

    def TransformFuncLambda(self,mathString):
        '''
        parse MathML to an executable function when the contenct MathML
        is in lambda function
        '''
        # remove the brackets
        eqn1 = mathString.replace('(',' ',1)
        eqn1 = Eqn1[:-1]
        eqn2 = eqn1[7:].split(', ')
        # find the seperation between variable assertion and function
        var1 = 0
        form = re.compile('[\w*]$')
        while form.match(eqn2[var1]):
            var1 = var1+1
            continue
        # parse the t to an excutable string
        self.eqn = ','.join(eqn2[var1:])
        self.eqnFs = 'lambda '+','.join(eqn2[0:var1])+':'+','.join(eqn2[var1:])
        self.eqnF = eval(self.eqnFs)
        return [self.eqnF,self.eqn]

    def TransformFuncNoLambda(self,mathString,var):
        '''
        parse MathML to an executable function when the contenct MathML
        is not in lambda function
        '''
        self.eqnFs = 'lambda '+','.join(var)+':'+mathString
        return self.eqnFs


class EqnProperty:
    '''
    Determine the dependences among equations
    '''
    def __init__(self):
        self.extendEqn = {}
        self.includeEqn = {}
        self.eqnAllType = {}

    def DetermineDependence(self, paraAll, varAll):
        '''
        Determine the dependences among equations
        '''
        # find out the equations whose output(s) is(are) the input(s)
        # of a given equation
        for [key, ele] in paraAll.iteritems():
            for [key1, ele1] in varAll.iteritems():
                self.includeEqn.setdefault(key,{})
                if (key!=key1) and (list(set(ele)&set(ele1))):
                    self.includeEqn.setdefault(key,{})
                    self.includeEqn[key][key1] = list(set(ele)&set(ele1))
        # find out the equations whose input(s) is(are) the output(s)
        # of a given equation
        for [key, ele] in varAll.iteritems():
            for [key1, ele1] in paraAll.iteritems():
                self.extendEqn.setdefault(key,{})
                if (key!=key1) and (list(set(ele)&set(ele1))):
                    self.extendEqn.setdefault(key,{})
                    self.extendEqn[key][key1] = list(set(ele)&set(ele1))
        return [self.extendEqn, self.includeEqn]

    def EqnType(self, includeEqn, eqnAll):
        '''
        Determine the types of method to solve an equation
        '''
        n = len(eqnAll)
        for ele in eqnAll:
            self.eqnAllType.setdefault(ele,{})
            if includeEqn[ele]:
                cashe = list(self.GenerateDependent(1, n, ele, includeEqn, [ele]))
                simultaneous = self.FindSimultaneous(cashe, ele)
                if simultaneous:
                    simultaneous.remove(ele)
                    dependent = list(set(includeEqn[ele].keys()) - set(simultaneous) & \
                                 set(includeEqn[ele].keys()))
                else:
                    simultaneous = []
                    dependent = includeEqn[ele].keys()
                self.eqnAllType[ele].setdefault('simultaneous',simultaneous)
                self.eqnAllType[ele].setdefault('dependent',dependent)
            else:
                self.eqnAllType[ele].setdefault('direct',[])
        return self.eqnAllType
                

    def GenerateDependent(self, n, nmax, target, includeEqn, path):
        '''
        Determine whether dependent equations are solved simulatneously
        with the target eqnations
        '''
        if n < nmax:
            for ele in includeEqn[target]:
               # print ele
                if ele in path:
                    pathre = ','.join(path[path.index(ele):])
                    yield pathre
                    continue
                path.append(ele)
                for ele1 in self.GenerateDependent(n+1, nmax, ele, includeEqn, path):
                    yield ele1
                path.remove(ele)

    def FindSimultaneous(self, cashe, target):
        '''
        Generate simultaneous equations based on GenerateDependent
        '''
        simul = []
        for ele in cashe:
            if target in ele:
                simul = ele.split(',')
                cashe.remove(ele)
                break
        if simul:
            for ele in cashe:
                cashe2 = ele.split(',') 
                if list(set(cashe2) & set(simul)):
                    simul.extend(cashe2)
                    simul = list(set(simul))
            return simul
        else:
            return None     
