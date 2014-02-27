
base_z_size = 1 #units
layers_per_unit = 100
start_speed = 10
max_speed = 500
base_speed = 100
increment = 10
z_layer = 1.0 / layers_per_unit * 1.0
output_file = 'exposure_test.gcode'
size = 20 #units

output = open('exposure_test.gcode','w')
#build a base
z = 0.0

def square(speed):
    data = "M101\n"
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (size,size,speed)
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (size,-1.0 * size,speed)
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (-1.0 * size,-1.0 *size,speed)
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (-1.0 * size,size,speed)
    return data

def write_layer(z, speed):
    output.write('M103\nG1 Z%.2f F%.2f\n' % (z , speed))
    output.write(square(speed))

# build base
while (z < base_z_size):
    write_layer(z, base_speed)
    z = z + z_layer

# build layers
for speed in range(start_speed, max_speed, increment):
    write_layer(z,speed)
    z = z + z_layer

print("complete")