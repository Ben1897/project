""" Numerical Methods """

# Authur: Peishi JIANG

class findRoot:
    '''
    find root
    '''
    
    def __init__(self):
        self.x = 0
    
    def NewtonRaphson(self,f):
        '''
        Apply Newton-Raphson algorithm to find a root of an function f = 0
        f: function, df: the derivative of f, e: error, x0: initial guess
        '''
        self.x = input('Initial guess: ')
        e = 99; h = 0.01
        while e > 0.01:
            df = (1.0/(2*h))*(f(self.x+h)-f(self.x-h))
            dx = - f(self.x)/df
            e = abs(2*dx/(2*self.x+dx))
            self.x = self.x + dx
        return self.x
