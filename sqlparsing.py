

from parsing import *
import re

tk = token
def kw(str): return token(str,flags=re.I)

def build_parser():

    exprList = Recursive()
    expr = Recursive()
    tableList = Recursive()
    table = Recursive()
    term = Recursive()
    selectStatement = Recursive()
    logTerm = Recursive()
    condition = Recursive()

    mulOp = tk(r"[*/]")
    addOp = tk(r"[\+\-]")

    binOp = tk(r"(?:<|>|<=|>=|=)")
    andOp = kw("AND")
    orOp  = kw("OR")

    ident = tk(r"\w+")
    callargs = tk(r"\(") + exprList + tk(r"\)") >> Defined()
    funcall  = ident + ~callargs >> Defined()

    term <<= funcall + mulOp + term | funcall
    expr <<= term + addOp  + expr | term
    exprList <<= expr + (-kw(",") + expr )[...] | Empty()
    
    column = expr + ~(-kw("AS") +  ident) >> Defined()
    selectList = column  + (-kw(",") + column )[...]
    table <<= ( ident | kw(r"\(") + selectStatement + kw(r"\)") )  + ~(kw("AS") + ident)
    tableList <<= table + (-kw(",") + table )[...] | Empty()

    binExpr   = funcall + binOp + funcall >> Defined()
    logTerm   <<= binExpr + andOp + logTerm | binExpr
    condition <<= logTerm + orOp  + condition | logTerm

    whereClause = kw("WHERE") + condition >> Defined()
    selectStatement = ( kw("SELECT") + selectList + kw("FROM") + tableList +
                        ~whereClause )
    
    selectStatement.rec_set_splicing()
    column.splicing(False)
    selectStatement.splicing(False)

    return selectStatement


def main():

    parser = build_parser()

    ret = parser.parse("select x   from t",0)
    print(ret)
    ret = parser.parse("select x,y from t",0)
    print(ret)
    ret = parser.parse("select x,y from t where x = 1",0)
    print(ret)
    ret = parser.parse("select x,y from t where x = 1 and y = 1",0)
    print(ret)
    
if __name__ == "__main__":
    main()
