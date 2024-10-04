import time
import board
import busio
import adafruit_vl53l0x

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor objects with unique addresses
sensor_length = adafruit_vl53l0x.VL53L0X(i2c, address=0x30)  # Change if necessary
sensor_width = adafruit_vl53l0x.VL53L0X(i2c, address=0x31)  # Change if necessary
# sensor_height = adafruit_vl53l0x.VL53L0X(i2c, address=0x2B)  # Change if necessary

# Function to read distance from a sensor
def read_distance(sensor):
    try:
        distance = sensor.range
        return distance / 100.0  # Convert to cm
    except Exception as e:
        print(f"Error reading distance: {e}")
        return None

# Variables to store measurements
empty_length = empty_width = empty_height = 0
filled_length = filled_width = filled_height = 0

# Setup function
def setup():
    global empty_length, empty_width, empty_height

    print("Measuring empty box dimensions...")
    time.sleep(1)

    # Measure empty box dimensions
    empty_length = read_distance(sensor_length)
    empty_width = read_distance(sensor_width)
    # empty_height = read_distance(sensor_height)
    empty_height = 0

    print("Empty Box Dimensions (cm):")
    print(f"Length: {empty_length:.2f}")
    print(f"Width: {empty_width:.2f}")
    print(f"Height: {empty_height:.2f}")
    
    print("Place the object inside the box and reset the program to measure the filled dimensions.")

# Main loop
def loop():
    global filled_length, filled_width, filled_height

    try:
        while True:
            print("Measuring filled box dimensions...")

            # Measure dimensions after placing the object
            filled_length = read_distance(sensor_length)
            filled_width = read_distance(sensor_width)
            # filled_height = read_distance(sensor_height)
            filled_height = 12.8

            # Calculate object dimensions by subtracting filled from empty
            object_length = max(0, empty_length - filled_length)
            object_width = max(0, empty_width - filled_width)
            object_height = max(0, empty_height - filled_height)

            # Calculate CBM (in cubic meters)
            cbm = (object_length * object_width * object_height) / 1000000.0  # Convert cm³ to m³

            # Output dimensions and CBM
            print("Object Dimensions (cm):")
            print(f"Length: {object_length:.2f}")
            print(f"Width: {object_width:.2f}")
            print(f"Height: {object_height:.2f}")

            print(f"CBM (Cubic Meters): {cbm:.6f}")  # Print CBM with 6 decimal places for precision

            time.sleep(5)  # Wait 5 seconds before the next measurement

    except KeyboardInterrupt:
        print("\nMeasurement stopped by User.")

# Run setup and loop
setup()
loop()
