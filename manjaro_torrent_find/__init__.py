import sys

__version__ = "0.3.4"


def errorNotify(exci, e):
    lineno = exci.tb_lineno
    fname = exci.tb_frame.f_code.co_name
    ename = type(e).__name__
    msg = f"{ename} Exception at line {lineno} in function {fname}: {e}"
    # log.error(msg)
    print(msg)


def errorRaise(exci, e):
    errorNotify(exci, e)
    raise


def errorExit(exci, e):
    errorNotify(exci, e)
    sys.exit(1)
