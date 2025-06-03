import os

# Always get absolute directory no matter where you're running
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')
STATE_FILE = os.path.join(DATA_DIR, 'training_state.json')
CHROMA_DIR = os.path.join(DATA_DIR, 'chroma_storage')

print(DATA_DIR)
print(STATE_FILE)
print(CHROMA_DIR)

# d:\AnalyticsReportApp\db-analytics\data
# d:\AnalyticsReportApp\db-analytics\data\training_state.json
# d:\AnalyticsReportApp\db-analytics\data\chroma_storage