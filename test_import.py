import traceback

try:
    import main
    print('MAIN IMPORT OK')
except Exception:
    traceback.print_exc()
    raise
