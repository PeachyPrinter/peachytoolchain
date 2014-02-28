import sys
import getopt

def square(speed, size):
    data = "M101\n"
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (size,size,speed)
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (size,-1.0 * size,speed)
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (-1.0 * size,-1.0 *size,speed)
    data = data + "G1 X%.2f Y%.2f F%.2f E1\n" % (-1.0 * size,size,speed)
    return data

def get_layer(z, speed, size):
    data = 'M103\nG1 Z%.2f F%.2f\n' % (z , speed)
    return data + square(speed, size)

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
    start_speed = 100
    max_speed = 1000
    layers_per_unit = 100
    speed_increment = 50
    output_file = 'exposure_test.gcode'

    try:
        for opt, arg in opts:
            if (opt == '--size'):
                size = int(arg)
            elif (opt == '--start_speed'):
                start_speed = int(arg)
            elif (opt == '--max_speed'):
                max_speed = int(arg)
            elif (opt == '--layers_per_unit'):
                layers_per_unit = int(arg)
            elif (opt == '--speed_increment'):
                speed_increment = int(arg)
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
    base_speed = 400
    z_layer = 1.0 / layers_per_unit * 1.0

    output = open(output_file,'w')
    #build a base
    z = 0.0

    # build base
    while (z < base_z_size):
        layer = get_layer(z, base_speed, size)
        output.write(layer)
        z = z + z_layer

    # build layers
    for speed in range(start_speed, max_speed, speed_increment):
        layer = get_layer(z, base_speed, size)
        output.write(layer)
        z = z + z_layer

    print("Complete: Gcode file is located at %s" % output_file)

if __name__ == "__main__":
    main()