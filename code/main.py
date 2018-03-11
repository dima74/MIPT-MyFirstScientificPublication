import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as sps
import skimage.measure
import mnist

class ConvolutionLayer:
    FILTER_SIZE = 3

    def forward(self, inputs, weights, biases):
        """
        :param input: (N, height, width, depth)
        :param weights: (NUMBER_FILTERS, FILTER_SIZE, FILTER_SIZE, depth)
        :param biases: (NUMBER_FILTERS)
        :return: (outputs, cache)
        """
        PADDING_SIZE = 1
        NUMBER_FILTERS = 7

        N, input_height, input_width, input_depth = inputs.shape
        assert input_height == input_width
        input_size = input_height
        output_size = input_size + 2 * PADDING_SIZE - (self.FILTER_SIZE - 1)

        outputs = []
        for input in inputs:
            input_padded = np.pad(input, PADDING_SIZE, 'constant')
            output = np.empty((NUMBER_FILTERS, output_size, output_size))
            for filter_index, filter_weight, filter_bias in enumerate(zip(weights, biases)):
                for i in range(output_size):
                    for j in range(output_size):
                        # filter_weight = np.zeros((FILTER_SIZE, FILTER_SIZE, input_depth))
                        # filter_bias = 0
                        filter_input = input_padded[i:i + self.FILTER_SIZE, j:j + self.FILTER_SIZE, :]
                        output[filter_index][i][j] = (filter_weight * filter_input).sum() + filter_bias
            outputs.append(output)

        cache = (inputs, weights, biases, outputs)
        return outputs, cache

    def backward(self, gradients, cache):
        pass

class ReluLayer:
    def forward(self, inputs):
        """
        :param inputs: (N, height, width, depth)
        :return: (outputs, cache)
        """
        outputs = np.maximum(inputs, 0)
        cache = (inputs, outputs)
        return outputs, cache

    def backward(self, gradients, cache):
        pass

class PoolingLayer:
    def forward(self, inputs):
        """
        :param inputs: (N, height, width, depth)
        :return: (outputs, cache)
        """
        outputs = []
        for input in inputs:
            skimage.measure.block_reduce(input, (2, 2), np.max)
        cache = (inputs, outputs)
        return outputs

class FCLayer:
    def forward(self, inputs, weights, biases):
        """
        :param inputs: (N, height, width, depth)
        :param weights: (C, height*width*depth)
            C --- number classes, C = 10
        :param biases: (C)
        :return: (outputs, cache)
        """
        C = 10

        outputs = []
        for input in inputs:
            input_flatten = input.flatten()
            output = weights @ input_flatten
            outputs.append(output)

        cache = (inputs, weights, biases, outputs)
        return outputs, cache

class SoftmaxLayer:
    def forward(self, inputs):
        """
        :param inputs: (N, C)
        :return: (outputs, cache)
        """

        outputs = []
        for input in inputs:
            input_exp = np.exp(input)
            output = input_exp / np.sum(input_exp)
            outputs.append(output)
        cache = (inputs, outputs)
        return outputs, cache

    def backward(self, gradients, cache):
        """
        :param gradients: (C)
        :param cache:
        :return:
        """
        pass


"""
INPUT -> [[CONV -> RELU]*2 -> POOL]*3 -> FC

           INPUT:   (32, 32,  1)

G 1 1,2    CONV:    (32, 32, 10)
G 1 1,2    RELU:    (32, 32, 10)
G 1        POOL:    (16, 16, 10)

G 2 1,2    CONV:    (16, 16, 20)
G 2 1,2    RELU:    (16, 16, 20)
G 2        POOL:    ( 8,  8, 20)

G 3 1,2    CONV:    ( 8,  8, 30)
G 3 1,2    RELU:    ( 8,  8, 30)
G 3        POOL:    ( 4,  4, 30)

           FC:      (10)
           SOFTMAX: (10) 
           OUtPUT:  (10) 
"""
class Model:
    def __init__(self):
        NUMBER_GROUPS1 = 3
        NUMBER_GROUPS2 = 2

        layers = []  # [(layer, parameters)
        for i in range(NUMBER_GROUPS1):
            for j in range(NUMBER_GROUPS2):
                # CONV
                number_filters = 10 * i
                weights = sps.norm.rvs(size=(number_filters, ConvolutionLayer.FILTER_SIZE, ConvolutionLayer.FILTER_SIZE))
                biases = np.zeros(number_filters)
                parameters = weights, biases
                layers.append([ConvolutionLayer(), parameters])

                # RELU
                layers.append(ReluLayer())

            # POOL
            layers.append(PoolingLayer())
        layers.append(FCLayer)
        layers.append(SoftmaxLayer)
        self.layers = layers

    def forward_pass(self, x_train):
        previous_layer_input = x_train
        caches = []
        for layer, layout_parameters in self.layers:
            outputs, cache = layer.forward(previous_layer_input, *layout_parameters)
            previous_layer_input = outputs
            caches.append(cache)
        outputs = previous_layer_input
        return outputs, caches

    def train(self, x_train, y_train):
        NUMBER_GRADIENT_ITERATIONS = 100
        GRADIENT_STEP = 1e-3
        NUMBER_CLASSES = 10

        assert x_train.shape == (28, 28, 1)
        for _ in range(NUMBER_GRADIENT_ITERATIONS):
            # forward pass
            outputs, caches = self.forward_pass(x_train)

            # derivative of loss of softmax outputs
            gradients_for_softmax_outputs = []
            for output, y in zip(outputs, y_train):
                output_right = np.zeros(NUMBER_CLASSES)
                output_right[y] = 1

                # loss = -np.log(output * output_right)
                # производная ошибки по вероятностям классов
                gradient_for_softmax_outputs = -(output_right / output)
                gradients_for_softmax_outputs.append(gradient_for_softmax_outputs)
            gradients_for_softmax_outputs = np.mean(gradients_for_softmax_outputs, axis=0)
            assert gradients_for_softmax_outputs.shape == (NUMBER_CLASSES,)

            # backward pass
            gradients_for_outputs = gradients_for_softmax_outputs
            for layer, layout_parameters, cache in reversed(zip(self.layers, caches)):
                gradients_for_inputs, gradients_for_parameters = layer.backward(gradients_for_outputs, cache)
                layout_parameters[...] = layout_parameters - GRADIENT_STEP * gradients_for_parameters
                gradients_for_outputs = gradients_for_inputs

    def predict(self, x):
        outputs, caches = self.forward_pass(x)
        return outputs


def main():
    # should be runned once to generate mnist.pkl (which is used by mnist.load())
    # mnist.init()
    x_train, y_train, x_test, y_test = mnist.load()
    x_train = x_train.reshape((-1, 28, 28))
    x_train = np.array([np.pad(x, 32 - 28, 'constant') for x in x_train])
    x_train = x_train.reshape((-1, 28, 28))

    model = Model()
    model.train(x_train, y_train)

main()
