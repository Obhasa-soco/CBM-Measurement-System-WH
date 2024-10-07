import time
import statistics
from hx711 import HX711  # Import the HX711 library

# Define GPIO pins for HX711
DT_PIN = 5   # Data Pin (DT) on GPIO 5
SCK_PIN = 6  # Clock Pin (SCK) on GPIO 6

# Initialize the HX711
hx = HX711(DT_PIN, SCK_PIN)
hx.set_reading_format("MSB", "MSB")  # Most Significant Bit first
hx.set_reference_unit(10)  # Calibration factor (adjust this after calibration)
hx.reset()
hx.tare()  # Tare the scale to set it to 0

# Filter parameters for precision
sample_size = 10  # Number of samples for moving average
weight_samples = []  # List to store weight samples

def get_stable_weight():
    global weight_samples
    # Read raw data
    value = hx.get_weight(1)  # Get average of 5 readings for each sample
    weight_kg = value / 1000.0  # Convert from grams to kilograms
    
    # Ensure no negative weight values
    if weight_kg < 0:
        weight_kg = 0

    # Store the sample in the list
    weight_samples.append(weight_kg)

    # Keep the list size fixed to the sample_size
    if len(weight_samples) > sample_size:
        weight_samples.pop(0)

    # Calculate the moving average for better stability
    stable_weight = statistics.mean(weight_samples)

    return round(stable_weight, 2)  # Return with 2 decimal places


if __name__ == "__main__":
    print("Taring scale... Please remove any weight.")
    time.sleep(2)
    print("Tare complete. Starting measurements.")

    try:
        while True:
            if(get_stable_weight() < 0.99):
                weight = 0
            else:
                weight = get_stable_weight()
                
            print(f"Weight: {weight:.2f} kg")
            time.sleep(0.5)  # Delay for stability

    except (KeyboardInterrupt, SystemExit):
        print("Exiting program.")
        hx.power_down()
        hx.power_up()
