import time
import board
import busio
import adafruit_vl53l0x
import statistics
from hx711 import HX711  # Import the HX711 library

# Initialize I2C bus for VL53L0X sensors
i2c = busio.I2C(board.SCL, board.SDA)

# Create VL53L0X sensor objects with unique addresses
sensor_length = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)  # Adjust address as necessary
sensor_width = adafruit_vl53l0x.VL53L0X(i2c, address=0x30)  # Adjust address as necessary

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
    value = hx.get_weight(1)  # Get a single reading from the load cell
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

def wait_for_stable_weight(stability_duration=2, tolerance=0.05):
    """Wait for the weight to stabilize for a given duration."""
    stable_start_time = None
    last_weight = get_stable_weight()

    while True:
        current_weight = get_stable_weight()
        # Check if the weight change is within tolerance
        if abs(current_weight - last_weight) <= tolerance:
            if stable_start_time is None:
                stable_start_time = time.time()  # Start counting stability time
            elif time.time() - stable_start_time >= stability_duration:
                return current_weight  # Weight is stable for the required time
        else:
            stable_start_time = None  # Reset stability timer if weight changes
        last_weight = current_weight
        time.sleep(0.5)

def barcode_reader():
    """Read barcode from HID device."""
    hid = {4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 
           11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 
           17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 
           23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 
           29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 
           35: '6', 36: '7', 37: '8', 38: '9', 39: '0', 44: ' ', 
           45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';', 
           52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'}

    hid2 = {4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 
             11: 'H', 12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M', 
             17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 
             23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X', 28: 'Y', 
             29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 
             35: '^', 36: '&', 37: '*', 38: '(', 39: ')', 44: ' ', 
             45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':', 
             52: '"', 53: '~', 54: '<', 55: '>', 56: '?'}

    try:
        with open('/dev/hidraw0', 'rb') as fp:
            ss = ""
            shift = False
            done = False

            while not done:
                buffer = fp.read(8)  # Read 8 bytes from the HID device
                
                for byte in buffer:
                    if byte > 0:  # Check if the byte is greater than 0
                        if byte == 40:  # Carriage return signifies the end of barcode
                            done = True
                            break

                        if shift:
                            if byte == 2:  # Shift key
                                shift = True
                            else:
                                ss += hid2.get(byte, '')  # Uppercase letters
                                shift = False
                        else:
                            if byte == 2:  # Shift key
                                shift = True
                            else:
                                ss += hid.get(byte, '')  # Lowercase letters

            return ss
    except IOError as e:
        print(f"Error reading from HID device: {e}")
        return ""

def main():
    print("Taring scale... Please remove any weight.")
    time.sleep(2)
    hx.tare()  # Tare the scale
    try:
        while True:
            # Wait for stable weight before scanning
            # barcode = barcode_reader()
            stable_weight = wait_for_stable_weight(stability_duration=2)

            # if stable_weight < 1 and barcode:
            #     validation = True
            # if stable_weight > 1 :#and barcode
            #     validation = True
            #     flag+=1
            # else:
            #     validation=False
            # # print(validation)
            # print(stable_weight)
            # print(barcode)

            # if not validation:
            print("Please Put the Box first")
            while stable_weight <1:
                stable_weight = wait_for_stable_weight(stability_duration=2)
            # else:
            # Weight is stable, now ready to scan
            print("Ready to scan")

            # Wait for barcode input
            barcode = barcode_reader()
            if barcode:  # Proceed only if barcode is read
                print(f"Barcode: {barcode}")
                print(f"Weight: {stable_weight:.2f} kg")

                # Measure dimensions
                length, width = sensor_length.range / 100.0, sensor_width.range / 100.0
                print(f"Length: {length:.2f} cm")
                print(f"Width: {width:.2f} cm")
                height = 12.8  # Assuming height is constant for now
                print(f"Height: {height:.2f} cm")

                # Calculate CBM
                cbm = (length * width * height) / 1000000  # Convert to cubic meters
                print(f"CBM: {cbm:.6f} m³")

            time.sleep(1)  # Short delay before next cycle

    except KeyboardInterrupt:
        print("Program terminated by user.")
        hx.power_down()
        hx.power_up()  # Reset HX711 power state

if __name__ == "__main__":
    main()
