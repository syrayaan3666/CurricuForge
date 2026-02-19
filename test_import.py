import traceback

try:
    import main
    from services.logger import get_logger
    logger = get_logger("test_import")
    logger.info('MAIN IMPORT OK')
except Exception:
    traceback.print_exc()
    raise
