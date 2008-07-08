from pyparsing import Combine, Literal, Word, delimitedList, Group, Optional,\
     oneOf, ZeroOrMore, OneOrMore, nums, alphas, alphanums,\
     StringStart, StringEnd, CaselessLiteral


##
# 12.02.2007, c
class TermParse( object ):
    def __str__( self ):
        ss = "%s\n" % self.__class__
        for key, val in self.__dict__.iteritems():
            ss += "  %s:\n    %s\n" % (key, self.__dict__[key])
        return ss

##
# 11.05.2006, c
# 01.08.2006
# 09.08.2006
# 12.02.2007
# 10.04.2007
# 23.04.2007
# 13.11.2007
def collectTerm( termDescs, lc, itps ):
    signs = {'+' : 1.0, '-': -1.0}
    def append( str, loc, toks ):
        sign = signs[toks.sign] * signs[lc[0]]
        termPrefix = itps.get( toks.termDesc.name, '' ) 
##        print toks, lc, termPrefix
##         print name, integral, region
        tp = TermParse()
        tp.integral = toks.termDesc.integral
        tp.region = toks.termDesc.region
        tp.flag = toks.termDesc.flag
        tp.sign = sign * float( toks.mul[0] )
        tp.name = termPrefix + toks.termDesc.name
        tp.args = toks.args
#        print tp
        termDescs.append( tp )
    return append

##
# 21.05.2006, c
def rhs( lc ):
    def aux( str, loc, toks ):
        if toks:
#            print toks
            lc[0] = '-'
    return aux
        
##
# c: 21.05.2006, r: 08.07.2008
def createBNF( termDescs, itps ):
    """termDescs .. list of TermParse objects (sign, termName, termArgNames)"""

    lc = ['+'] # Linear combination context.
    equal = Literal( "=" ).setParseAction( rhs( lc ) )
    zero  = Literal( "0" ).suppress()

    point = Literal( "." )
    e = CaselessLiteral( "E" )
    inumber = Word( nums )
    fnumber = Combine( Word( "+-"+nums, nums ) + 
                       Optional( point + Optional( Word( nums ) ) ) +
                       Optional( e + Word( "+-"+nums, nums ) ) )


    ident = Word( alphas, alphanums + "_")
    variable = Word( alphas, alphanums + '._' )
    flag = Literal( 'a' )

    term = Optional( Literal( '+' ) | Literal( '-' ), default = '+' )( "sign" )\
           + Optional( fnumber + Literal( '*' ).suppress(),
                       default = '1.0' )( "mul" ) \
           + Combine( ident( "name" )\
                      + Optional( "." + (ident( "integral" ) + "."
                                  + ident( "region" ) + "." + flag( "flag" ) |
                                  ident( "integral" ) + "." + ident( "region" ) |
                                  ident( "region" )
                                  )))( "termDesc" ) + "("\
                                  + Optional( delimitedList( variable ),
                                default = [] )( "args" ) + ")"
    term.setParseAction( collectTerm( termDescs, lc, itps ) )

    rhs1 = equal + OneOrMore( term )
    rhs2 = equal + zero
    equation = StringStart() + OneOrMore( term )\
               + Optional( rhs1 | rhs2 ) + StringEnd()

#    term.setDebug()

    return equation
    
    
if __name__ == "__main__":

    testStr = """d_term1.Y( fluid, u, w, Nu, dcf, mode )
                 + 5.0 * d_term2.Omega( u, w, Nu, dcf, mode )
                 - d_another_term.Elsewhere( w, p, Nu, dcf, mode )
                 = - dw_rhs.Y3.a( u, q, Nu, dcf, mode )"""
    
    termDescs = []
    bnf = createBNF( termDescs, {} )
    out = bnf.parseString( testStr )

    print 'out:', out, '\n'
    for tp in termDescs:
        print tp
