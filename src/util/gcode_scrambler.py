gIn=open("unsort.gcode","r") #open input gcode file
l=0 #layer number. (0 is before first layer)

list = [0] #list that will contain layers (layers contain g-code lines) (ie. l by g matrix)

new_z=0 #Original code will go to new z levels
randomize_z=-1  #When a new z is seen, this counter starts at a random number based on the number of gcodes in the last layer. Counts down to 0 
gcodes_in_this_layer=0
gcodes_in_last_layer=2
from random import randrange

#Input layers into matrix:
#for every line in input file:
for line in gIn:
	
	#find new layer:
	if (line[:6]) == ";LAYER":
		if gcodes_in_this_layer>1:
			gcodes_in_last_layer=gcodes_in_this_layer
		gcodes_in_this_layer=0
		l=l+1
		list.append([]) #add list for new layer
	 
	#find line starting in "G" (peachy only needs these)
	if (line[:2]) == "G1": 
		gcodes_in_this_layer=gcodes_in_this_layer+1
		if new_z==0 or randomize_z!=0:
			list[l].append(line)
			randomize_z=randomize_z-1
		else:
			list[l].append(line[:line.index('\n')]+' '+new_z)
			new_z=0
		
	if (line[:2]) == "G0": 
		if line.find('Z')>0:
			new_z= line[line.index('Z'):]
			randomize_z=randrange(1,gcodes_in_last_layer)


#randomize starting point of one layer:
def rand(inp):
	a = len(inp) #number of lines in layer
	p=0 # new counter variable when past end of input list, go back to inp[p]
	out=[]
	ran= randrange(1,a+1) #random start integer of the layer

	for i in range(0,a):
		#starting at random index of input until end of input list:
		if i+ran<a+1:

			if i==0: #remove extrude command from end of line for first point
				if inp[ran-1].find('E') >0:	
					inp[ran-1]=inp[ran-1][:inp[ran-1].index('E')]+"\n"

			out.append(inp[i+ran-1])

		#past end of input list, go back to 0 and then iterate 1,2,3.. until i out of range
		else:
			if p==0:
				out.append(";original start of layer: \n")
			out.append(inp[p])
			p=p+1
	return out

gIn.close() #close input gcode file


#call randomizer for each layer:
for i in range(len(list)):
	if i>0:
		list[i]= rand(list[i])


#open file to write to:
gOut=open("test_mar_20.gcode","w")

#write to file, separating with layer comment
for i in range(1,len(list)):
	gOut.write(";LAYER:"+str(i)+"\n")
	for j in range(0,len(list[i])):
		gOut.write(list[i][j])

gOut.close() #close output gcode file




