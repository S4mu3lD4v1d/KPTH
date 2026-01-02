from celery import Celery
from kafka import KafkaConsumer
import json
import os
import numpy as np
from scipy import stats

app = Celery('worker', broker=f'kafka://{os.getenv("REDPANDA_BROKERS")}')

@app.task
def analyze_data(data):
    # Real-time analysis logic for climate change
    print(f"Analyzing: {data}")
    # Example: Trend analysis on temperature data
    # Assume data has 'values' list
    if 'values' in data:
        values = np.array(data['values'])
        slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(values)), values)
        trend = "increasing" if slope > 0 else "decreasing"
        analysis = {
            "trend": trend,
            "slope": slope,
            "r_squared": r_value**2,
            "p_value": p_value,
            "climate_impact": "significant" if p_value < 0.05 else "insignificant"
        }
        print(f"Climate analysis: {analysis}")
        # Store or alert
    return {"analysis": "completed"}

# Consumer for real-time processing
def consume_and_analyze():
    consumer = KafkaConsumer(
        "data_topic",
        bootstrap_servers=os.getenv("REDPANDA_BROKERS"),
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    for message in consumer:
        analyze_data.delay(message.value)

if __name__ == "__main__":
    import threading
    threading.Thread(target=consume_and_analyze, daemon=True).start()
    app.start()