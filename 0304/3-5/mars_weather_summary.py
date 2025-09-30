import matplotlib.pyplot as plt
import mysql.connector

PARENT_PATH = '0304/3-5/'
CSV_FILE_PATH = PARENT_PATH + 'mars_weathers_data.CSV'
RESULTS_PATH = PARENT_PATH + 'mars_weather_summary.png'


class MySQLHelper:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self.cursor = self.connection.cursor()

    def execute(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)

    def executemany(self, query, values_list):
        self.cursor.executemany(query, values_list)

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()


def read_csv(file_path):
    data = []
    try:
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    if not lines:
        return []

    headers = lines[0].strip().split(',')
    required_fields = {'mars_date', 'temp', 'storm'}
    if not required_fields.issubset(headers):
        return []

    idx_map = {key: headers.index(key) for key in required_fields}
    for line_number, line in enumerate(lines[1:], start=2):
        parts = line.strip().split(',')
        if len(parts) != len(headers):
            continue

        try:
            date = parts[idx_map['mars_date']]
            temp = round(float(parts[idx_map['temp']]))
            storm = int(parts[idx_map['storm']])
            data.append((date, temp, storm))
        except (ValueError, IndexError) as e:
            print(f'Error processing line {line_number}: {e}')

    return data


def insert_data(db_helper, data):
    insert_query = """
        INSERT INTO mars_weather (mars_date, temp, storm)
        VALUES (%s, %s, %s)
    """
    # for row in data:
    #     try:
    #         db_helper.execute(insert_query, row)
    #     except Exception as e:
    #         print(f'Error inserting row {row}: {e}')
    db_helper.executemany(insert_query, data)
    db_helper.commit()


def visualize_data(db_helper):
    db_helper.execute(
        'SELECT mars_date, temp, storm FROM mars_weather ORDER BY mars_date'
    )
    rows = db_helper.fetchall()
    dates, temps, storms = zip(*rows, strict=False)
    print(f'Fetched {len(rows)} records from the database')

    fig, ax1 = plt.subplots(figsize=(30, 6))

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)', color='tab:blue')
    ax1.plot(
        dates,
        temps,
        color='tab:blue',
        marker='o',
        markersize=3,
        linewidth=1,
        label='Temperature',
    )
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Storm Level', color='tab:red')
    ax2.plot(
        dates,
        storms,
        color='tab:red',
        marker='x',
        markersize=3,
        linewidth=1,
        label='Storm',
    )
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title('Mars Weather: Temperature & Storm Over Time')
    fig.tight_layout()
    plt.xticks(rotation=45)
    plt.savefig(RESULTS_PATH)
    plt.close()


def main():
    try:
        db_helper = MySQLHelper(
            host='localhost', user='mars', password='mars', database='mars_db'
        )

        data = read_csv(CSV_FILE_PATH)
        insert_data(db_helper, data)
        visualize_data(db_helper)
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    finally:
        if 'db_helper' in locals():
            db_helper.close()
        print('Database connection closed')


if __name__ == '__main__':
    main()
