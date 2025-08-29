import pandas as pd
pin_table_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSxj3JT6EABDUgFf5RpNZIOyjmZz3Dl7S7QBn7IkNJgQFUEoNI14sn_1hdoIiEM-R0L0GYIwjkseEDs/pub?gid=1605553209&single=true&output=csv"
pin_table = pd.read_csv(pin_table_url)

def map_type(instance):
    if "inout_i" in instance:
        return "bidirectional"
    if "output_i" in instance:
        return "output"
    if "input_i" in instance: 
        return "input"
    return "power_in"

def map_side(a):
    # supply pins on top
    if a.pin_class in [1,3,5,8]:
        return "top"
    # ground pins on the bottom
    if a.pin_class in [2,4,6]: 
        return "bottom"
    # gpios and blade on the right side
    if a.unit in ["gpio", "blade"]:
        return "right"
    # everything else left
    return "left"

pin_table["pin_class"] = pin_table.apply(lambda x: 8 if "bladetest_vdd" in x.pin_name else x.pin_class, axis=1)

valid_pins = pin_table[pin_table.pin_class > 0].sort_values(["unit", "pin_class", "QFN_pin_number"]).copy()
valid_pins["Type"] = valid_pins.instance.apply(map_type)
valid_pins["Side"] = valid_pins.apply(map_side, axis=1)
valid_pins["Name"] = valid_pins.pin_name
valid_pins["Pin"] = valid_pins.QFN_pin_number.apply(int)

output = valid_pins[["Pin", "Type", "Name", "Side"]]
with open("heepocrates.csv", "w") as f:
    f.write("heepocrates\n\n")
    f.write(output.set_index("Pin").to_csv())
