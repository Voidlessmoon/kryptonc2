from src.cnc import start as start_cnc
from src.utils.logger import Logger

if __name__ == '__main__':
    # Initialize logger
    logger = Logger()
    
    try:
        logger.info("Starting Krypton C2 server...")
        start_cnc()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Critical error occurred: {str(e)}")
    finally:
        logger.info("Server shutdown complete")