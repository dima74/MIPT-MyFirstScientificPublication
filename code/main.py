import numpy as np
import matplotlib.pyplot as plt

import mnist

# should be runned once to generate mnist.pkl (which is used by mnist.load())
# mnist.init()
x_train, y_train, x_test, y_test = mnist.load()

x_train = x_train.reshape((-1, 28, 28, 1))

x = x_train[0]

# CONV
FILTER_SIZE = 3
PADDING_SIZE = 1
NUMBER_FILTERS = 7

conv_input_depth = x.shape[2]
conv_input_size = x.shape[0]
conv_output_size = conv_input_size + 2 * PADDING_SIZE - (FILTER_SIZE - 1)

conv_input = x
conv_padded = np.pad(conv_input, PADDING_SIZE, 'constant')
conv_output = np.empty((conv_output_size, conv_output_size))
for i in range(conv_output_size):
    for j in range(conv_output_size):
        filter_weights = np.zeros((FILTER_SIZE, FILTER_SIZE, conv_input_depth))
        filter_bias = 0
        filter_input = conv_input[i:i + FILTER_SIZE, j:j + FILTER_SIZE, :]
        conv_output[i][j] = (filter_weights * filter_input).sum() + filter_bias

# RELU
relu_input = conv_output
relu_output = np.max(relu_input, 0)

# POOL
pool_input = relu_output
pool_output = pool_input[::2, ::2]

# FC
fc_input = pool_output
fc_input_flatten = fc_input.flatten()

fc_input_length = len(fc_input_flatten)
fc_weights = np.zeros((fc_input_length, fc_input_length))

fc_output_flatted = (fc_weights @ fc_input_flatten)
fc_output = fc_output_flatted.reshape(fc_input.shape)

# OUPUT
output = fc_output
