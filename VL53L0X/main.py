import time
import board
import busio
import digitalio
import adafruit_vl53l0x

# Setup I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Setup shutdown pins for each sensor
shut1 = digitalio.DigitalInOut(board.D16)  # GPIO16 for Sensor 1
shut2 = digitalio.DigitalInOut(board.D17)  # GPIO17 for Sensor 2

shut1.direction = digitalio.Direction.OUTPUT
shut2.direction = digitalio.Direction.OUTPUT

# Turn off both sensors first
shut1.value = False
shut2.value = False

time.sleep(1)  # Give sensors time to shut down

# Helper function to initialize each sensor with a unique I2C address
def init_sensor(shut_pin, new_address):
    shut_pin.value = True  # Turn on the sensor
    time.sleep(0.1)  # Wait for sensor to start
    sensor = adafruit_vl53l0x.VL53L0X(i2c)  # Initialize sensor
    sensor.set_address(new_address)  # Set a new address
    
    # High-accuracy mode (longer ranging period but better precision)
    sensor.measurement_timing_budget = 200000  # Set to 200 ms
    
    return sensor

# Initialize each sensor with different addresses
sensor1 = init_sensor(shut1, 0x30)
sensor2 = init_sensor(shut2, 0x29)

# Function to take multiple readings and average them for more accurate results
def get_average_reading(sensor, num_samples=5):
    readings = []
    for _ in range(num_samples):
        try:
            readings.append(sensor.range)
        except RuntimeError:
            print("Error reading from sensor")
        time.sleep(0.05)  # Short delay between readings
    # Return the average in centimeters, formatted to 2 decimal places
    return round(sum(readings) / len(readings) / 10.0, 2)  # mm to cm, rounded

# Main loop to read and display data from both sensors
while True:
    try:
        # Take and print averaged readings from each sensor
        dist1 = get_average_reading(sensor1)
        dist2 = get_average_reading(sensor2)
        
        print(f"Sensor 1: {dist1:.2f} cm")
        print(f"Sensor 2: {dist2:.2f} cm")
        
    except RuntimeError:
        print("Error reading sensor data")
    
    time.sleep(1)  # Wait before taking the next reading