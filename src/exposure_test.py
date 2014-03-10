import sys
import getopt

def to_mm_per_minute(mm_per_second):
    return mm_per_second / 60.0

def square(speed, rapid_speed, size):
    data = ""
    data = data + "G1 X%.2f Y%.2f F%.2f\n" % (-1.0 * size, -1.0 * size,rapid_speed)
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (1.0 * size, -1.0 * size,speed)
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (1.0 * size, 1.0 * size, speed)

    return data

def get_layer(z, speed, rapid_speed, size):
    data = 'G1 Z%.2f F%.2f\n' % (z , speed)
    return data + square(speed, rapid_speed, size)

def usage():
    print("Usage:\npython exposure_test.py --size=(1/2 print area recommended)")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h' , ['help', 'size=', 'start_speed=','max_speed=','layers_per_unit=','speed_increment=','output_file='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    #Defaults
    size = 5
    start_speed = to_mm_per_minute(100)
    max_speed = to_mm_per_minute(1000)
    layers_per_unit = 10
    speed_increment = to_mm_per_minute(5)
    output_file = 'exposure_test.gcode'

    try:
        for opt, arg in opts:
            if (opt == '--size'):
                size = int(arg)
            elif (opt == '--start_speed'):
                start_speed = to_mm_per_minute(int(arg))
            elif (opt == '--max_speed'):
                max_speed = to_mm_per_minute(int(arg))
            elif (opt == '--layers_per_unit'):
                layers_per_unit = int(arg)
            elif (opt == '--speed_increment'):
                speed_increment = to_mm_per_minute(int(arg))
            elif (opt == '--output_file'):
                output_file = arg
            else:
                usage()
                exit(2)

    except Exception as ex:
        print(ex)
        usage()
        exit(2)


    base_z_size = 3 #units
    base_speed = start_speed + ((max_speed - start_speed) / 2)
    z_layer = 1.0 / layers_per_unit * 1.0

    output = open(output_file,'w')
    #build a base
    z = z_layer # gcode to wave can't handle 0.0 start point

    # build base
    while (z < base_z_size):
        layer = get_layer(z, base_speed, max_speed, size)
        output.write(layer)
        z = z + z_layer

    # build layers
    for speed in range(start_speed, max_speed, speed_increment):
        layer = get_layer(z, speed, max_speed, size)
        output.write(layer)
        z = z + z_layer

    print("ZUnits = " + str(z))
    output.close()

    print("Complete: Gcode file is located at %s" % output_file)

if __name__ == "__main__":
    main()