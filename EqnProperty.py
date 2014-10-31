"""Determine the dependences among equations"""

from libsbml import *
import operator as op
import re
from math import *
from os import listdir
from pprint import pprint
import itertools

class EqnProperty:

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

    
