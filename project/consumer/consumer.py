from consumer_pg import main as pg
from consumer_spark import main as sp

import threading
import time


def run_pg():
    """Runs the PostgreSQL consumer in a separate thread."""
    pg()


def run_sp():
    """Runs the Spark consumer in a separate thread."""
    sp()


if __name__ == "__main__":
    """Runs Stream data consuming in two threads."""
    time.sleep(60)

    # Create threads for each function
    pg_thread = threading.Thread(target=run_pg)
    sp_thread = threading.Thread(target=run_sp)

    # Start the threads
    pg_thread.start()
    sp_thread.start()

    # Wait for both threads to complete
    pg_thread.join()
    sp_thread.join()
