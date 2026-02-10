#!/Users/sky/venv/bin/python
import oracledb
import multiprocessing
import time
import os
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# DB Config (defaults based on existing scripts)
DB_CONFIG = {
    "user": os.getenv("ORA_USER", "your_username"),
    "password": os.getenv("ORA_PASSWORD", "your_password"),
    "dsn": os.getenv("ORA_DSN", "your_host:1521/your_service_name")
}

INSERT_SQL = """
INSERT INTO BILL_SYNC_CACHE_SUCCESS_REVERSE 
(TRANS_ID, CUST_ID, ORDER_ITEM_ID, REQUEST, CREATE_DATE, PART_ID, PROCESS_DATE)
VALUES (:1, :2, :3, :4, :5, :6, :7)
"""

BATCH_SIZE = 100000
DEFAULT_TOTAL_RECORDS = 100_000_000

def insert_worker(process_id, num_records):
    """Worker function for parallel insertion."""
    try:
        conn = oracledb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        records_inserted = 0
        start_time = time.time()
        
        logger.info(f"Process {process_id} starting insertion of {num_records} records.")
        
        while records_inserted < num_records:
            current_batch_size = min(BATCH_SIZE, num_records - records_inserted)
            batch_data = []
            
            # Generate dummy data
            # Use a base timestamp once per batch to save calculations
            run_id = int(time.time() % 10**6) 
            for i in range(current_batch_size):
                # Unique 18-digit ID: 6-digit time + 2-digit proc + 9-digit seq
                seq_id = records_inserted + i
                trans_id = (run_id * 10**12) + (process_id * 10**9) + seq_id
                
                cust_id = random.randint(10000000, 99999999)
                order_item_id = random.randint(10000000, 99999999)
                request_data = f"REQ_{trans_id}_PAYLOAD_DATA_FOR_PERF_TESTING"
                create_date = datetime.now()
                part_id = random.randint(1, 12)
                process_date = datetime.now()
                
                batch_data.append((trans_id, cust_id, order_item_id, request_data, create_date, part_id, process_date))
            
            # Execute batch insert
            cursor.executemany(INSERT_SQL, batch_data)
            conn.commit()
            
            records_inserted += current_batch_size
            
            # Progress reporting
            if records_inserted % 500_000 == 0 or records_inserted == num_records:
                elapsed = time.time() - start_time
                rps = records_inserted / elapsed if elapsed > 0 else 0
                logger.info(f"Process {process_id}: {records_inserted}/{num_records} inserted. Current RPS: {rps:.2f}")
                
        cursor.close()
        conn.close()
        logger.info(f"Process {process_id} completed insertion.")
        
    except Exception as e:
        logger.error(f"Error in process {process_id}: {e}")

def run_performance_test(total_records=DEFAULT_TOTAL_RECORDS, num_processes=None):
    if num_processes is None:
        num_processes = os.cpu_count() or 4
        
    records_per_process = total_records // num_processes
    
    logger.info("=" * 50)
    logger.info(f"STARTING PERFORMANCE TEST: {total_records} RECORDS")
    logger.info(f"Processes: {num_processes}, Batch Size: {BATCH_SIZE}")
    logger.info("-" * 50)
    
    start_time = time.time()
    
    processes = []
    for i in range(num_processes):
        p = multiprocessing.Process(target=insert_worker, args=(i, records_per_process), name=f"Worker-{i}")
        processes.append(p)
        p.start()
        
    for p in processes:
        p.join()
        
    total_time = time.time() - start_time
    logger.info("-" * 50)
    logger.info(f"PERFORMANCE TEST COMPLETED")
    logger.info(f"Total Time: {total_time:.2f} seconds")
    logger.info(f"Overall RPS: {total_records / total_time:.2f}")
    logger.info("=" * 50)

if __name__ == "__main__":
    import sys
    # Allow passing record count as argument
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000 # Default to 1M for safety if run without args
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    run_performance_test(total_records=count, num_processes=procs)
