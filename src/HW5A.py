import numpy as np
import random
import math

# 40 weights of the hidden layer
# bias0, weightA0, weightB0, weightC0, weightD0, bias1, weightA1, weightB1, weightC1, ...,
# bias7, weightA7, weightB7, weightC7, weightD7 (where ABCD are inputs)
# assigned random value from -1.0 to 1.0 rounded to 1 decimal place
hidden_weights = []
for i in range(40):
    hidden_weights.append(round(random.uniform(-1.0, 1.0), 1))
# print(len(hidden_weights))

# 9 weights in the outer layer; 1 for bias, eight for the outpuer of the eight hidden nodes
# outer_weights[0] = bias, the rest are for the nodes
outer_weights = []
for i in range(9):
    outer_weights.append(round(random.uniform(-1.0, 1.0), 1))
# print(len(outer_weights))

all_inputs = np.array([[0,0,0,0],
                       [0,0,0,1],
                       [0,0,1,0],
                       [0,0,1,1],
                       [0,1,0,0],
                       [0,1,0,1],
                       [0,1,1,0],
                       [0,1,1,1],
                       [1,0,0,0],
                       [1,0,0,1],
                       [1,0,1,0],
                       [1,0,1,1],
                       [1,1,0,0],
                       [1,1,0,1],
                       [1,1,1,0],
                       [1,1,1,1]])
# print(all_inputs)
# print(all_inputs[1])
                
expected_outputs = np.array([[0,1,0,1,0,1,0,1,1,1,1,1,0,0,0,1]]).T
# print(expected_outputs)
# print(expected_outputs[1])

# sigmoid function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# goes through the hidden weights multiplying the input by the weights
# uses counter as an incrementer to go through every (where ABCD are inputs)
# 5 weights (bias, weightA, weightB, weightC, weightD) then sigmoid and 
# repeats 8 times 8*5 = 40 
# then uses these values to multiply with the outer_weights and then sigmoid
# the sum to get the output of the network
def get_input_sum(input_array):
    counter = 0
    before_sigmoid = []
    for i in range(8):
        sum = (hidden_weights[counter] + \
        (hidden_weights[counter+1] * input_array[0]) + \
        (hidden_weights[counter+2] * input_array[1]) + \
        (hidden_weights[counter+3] * input_array[2]) + \
        (hidden_weights[counter+4] * input_array[3]))
        before_sigmoid.append(sum)
        counter = counter + 5

    return before_sigmoid

def get_hidden_outputs(input_array):
    before_sigmoid = get_input_sum(input_array)
    for_output_layer = []
    for i in range(len(before_sigmoid)):
        for_output_layer.append(sigmoid(before_sigmoid[i]))

    return for_output_layer

def output_method(input_array):
    for_output_layer = get_hidden_outputs(input_array)
    outer_sum = outer_weights[0]
    for i in range(len(for_output_layer)):
        outer_sum = outer_sum + (for_output_layer[i] * outer_weights[i+1])

    return sigmoid(outer_sum)

# val = random from all_inputs corresponding with expected_outputs?
def backprop(val):
    alpha = 0.75
    # Step 2 in slides
    a = output_method(all_inputs[val])
    # Step 3 in slides
    error_output_node = expected_outputs[val][0] - a
    # Step 4 in slides
    delta_output_node = error_output_node * a * (1 - a)
    # Step 5 in slides
    hidden_errors = []
    for i in range(1, len(outer_weights)):
        hidden_errors.append(outer_weights[i] * delta_output_node)
    # Step 6 in slides
    hidden_deltas = []
    hidden_outputs = get_hidden_outputs(all_inputs[val])
    for i in range(len(hidden_errors)):
        hidden_deltas.append(hidden_errors[i] * hidden_outputs[i] * (1 - hidden_outputs[i]))
    # Step 7 in slides
        # change the outer layer weights
        # change bias differently with x as 1 rather than x as hidden_outputs[i-1]
    for i in range(len(outer_weights)):
        if(i == 0):
            outer_weights[i] = outer_weights[i] + (alpha * delta_output_node)
        else:
            outer_weights[i] = outer_weights[i] + (alpha * delta_output_node * hidden_outputs[i-1])
    
    for i in range(len(hidden_weights)):
        j = 0
        if(i < 5):
            j = 0
        elif(i < 10):
            j = 1
        elif(i < 15):
            j = 2
        elif(i < 20):
            j = 3
        elif(i < 25):
            j = 4
        elif(i < 30):
            j = 5
        elif(i < 35):
            j = 6
        else:
            j = 7
        if((i%5) == 0):
            hidden_weights[i] = hidden_weights[i] + (alpha * hidden_deltas[j])
        else:
            hidden_weights[i] = hidden_weights[i] + (alpha * hidden_deltas[j] * all_inputs[val][(i%5)-1])

    return error_output_node
        

# testing output_method but not for accuracy
inps = [0,0,0,0]
inps2 = [1,1,1,1]
# print(output_method(inps))
# print(output_method(inps2))

# trying out some stuff to test backprop
error = 1
inputs = np.array([-1, -1, -1, -1, -1,
                  -1, -1, -1, -1, -1])
print("Inputs:")
for i in range(len(inputs)):
    inputs[i] = random.randint(0,15)
    print(inputs[i])
print("Error Values after each epoch:")
while (abs(error/10) > 0.05):
    error = 0
    for i in range(len(inputs)):
        error = abs(error) + abs(backprop(inputs[i]))
    print(error/10)