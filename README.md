# Oracle Performance Insertion Toolkit

A set of Python scripts designed to test and benchmark high-volume data insertion performance in Oracle databases. These scripts use `multiprocessing` and `python-oracledb` to achieve high Requests Per Second (RPS) metrics.

## Scripts

- **[performance_insert_100m.py](file:///Users/sky/Dropbox/ApplicationSync/Pycharm/WorkingHelp/PerformanceInsertion/performance_insert_100m.py)**: Inserts records into the `BILL_SYNC_CACHE_SUCCESS` table.
- **[performance_insert_100m_REVERSE.py](file:///Users/sky/Dropbox/ApplicationSync/Pycharm/WorkingHelp/PerformanceInsertion/performance_insert_100m_REVERSE.py)**: Inserts records into the `BILL_SYNC_CACHE_SUCCESS_REVERSE` table.

## Prerequisites

- Python 3.x
- `python-oracledb` library
- Access to an Oracle database

## Configuration

The scripts use environment variables for database connectivity. If not provided, they fall back to default values.

| Variable | Description | Default Value |
| :--- | :--- | :--- |
| `ORA_USER` | Database username | `your_username` |
| `ORA_PASSWORD` | Database password | `your_password` |
| `ORA_DSN` | Connection string (DSN) | `your_host:1521/your_service_name` |

## Usage

You can run the scripts directly from the command line. You can specify the total number of records to insert and the number of parallel processes.

### Basic Usage (Default 1M records)

```bash
python performance_insert_100m.py
```

### Advanced Usage

```bash
# Insert 10 million records using 8 parallel processes
python performance_insert_100m.py 10000000 8
```

## Implementation Details

- **Multiprocessing**: Uses `multiprocessing.Process` to bypass Python's GIL and utilize multiple CPU cores for simultaneous database connections.
- **Batch Insertion**: Uses `cursor.executemany()` with a default `BATCH_SIZE` of 100,000 for efficient networking and database resource utilization.
- **Data Generation**: Generates 18-digit unique `TRANS_ID` values based on a combination of timestamp, process ID, and local sequence.
- **Progress Monitoring**: Logs real-time insertion progress and current RPS (Records Per Second) per worker and overall.

## Target Tables Schema

The scripts expect a table with the following structure:

| Column | Type |
| :--- | :--- |
| `TRANS_ID` | NUMBER(18) |
| `CUST_ID` | NUMBER |
| `ORDER_ITEM_ID` | NUMBER |
| `REQUEST` | CLOB |
| `CREATE_DATE` | DATE |
| `PART_ID` | NUMBER |
| `PROCESS_DATE` | DATE |
