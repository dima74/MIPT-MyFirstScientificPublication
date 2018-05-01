import numpy as np
import scipy.stats as sps
import skimage.measure
from CNN_without_libraries import mnist

NUMBER_CLASSES = 10


class ConvolutionLayer:
    FILTER_SIZE = 3
    PADDING_SIZE = 1

    def forward(self, inputs, weights, biases):
        """
        :param inputs: (N, height, width, depth)
        :param weights: (NUMBER_FILTERS, FILTER_SIZE, FILTER_SIZE, depth)
        :param biases: (NUMBER_FILTERS)
        :return: (outputs, cache)
            outputs: (N, height, width, NUMBER_FILTERS)
            cache: (inputs, weights, biases, outputs)
        """
        N, input_height, input_width, input_depth = inputs.shape
        assert input_height == input_width
        input_size = input_height
        output_size = input_size + 2 * self.PADDING_SIZE - (self.FILTER_SIZE - 1)

        number_filters = weights.shape[0]
        assert weights.shape == (number_filters, self.FILTER_SIZE, self.FILTER_SIZE, input_depth)
        assert biases.shape == (number_filters,)

        outputs = []
        for input in inputs:
            input_padded = np.pad(input, self.PADDING_SIZE, 'constant')
            output = np.empty((number_filters, output_size, output_size))
            for filter_index, filter_weight, filter_bias in enumerate(zip(weights, biases)):
                for i in range(output_size):
                    for j in range(output_size):
                        assert filter_weight.shape == (self.FILTER_SIZE, self.FILTER_SIZE, input_depth)
                        filter_input = input_padded[i:i + self.FILTER_SIZE, j:j + self.FILTER_SIZE, :]
                        output[filter_index][i][j] = (filter_weight * filter_input).sum() + filter_bias
            outputs.append(output)
        outputs = np.array(outputs)
        cache = (inputs, weights, biases, outputs)
        return outputs, cache

    def backward(self, gradients_for_outputs, cache):
        """
        :param gradients_for_outputs: (N, depth, height, width)
        :param cache: (inputs, weights, biases, outputs)
        :return: (gradients_for_inputs, gradients_for_parameters)
            gradients_for_inputs: (N, depth, height, width)
            gradients_for_parameters: (gradients_for_weights, gradients_for_biases)
                gradients_for_weights: (C, height*width*depth)
                gradients_for_biases: (C)
        """
        pass


class ReluLayer:
    def forward(self, inputs):
        """
        :param inputs: (N, height, width, depth)
        :return: (outputs, cache)
            outputs: (N, height, width, depth)
            cache: (inputs, outputs)
        """
        outputs = np.maximum(inputs, 0)
        cache = (inputs, outputs)
        return outputs, cache

    def backward(self, gradients_for_outputs, cache):
        """
        :param gradients_for_outputs: (N, depth, height, width)
        :param cache: (inputs, outputs)
        :return: (gradients_for_inputs, gradients_for_parameters)
            gradients_for_inputs: (N, depth, height, width)
            gradients_for_parameters: []
        """
        inputs, outputs = cache
        mask = inputs == outputs  # == (inputs >= 0)
        gradients_for_inputs = gradients_for_outputs * mask
        return gradients_for_inputs, []


class PoolingLayer:
    def forward(self, inputs):
        """
        :param inputs: (N, height, width, depth)
        :return: (outputs, cache)
            outputs: (N, height/2, width/2, depth)
            cache: (inputs, outputs)
        """
        outputs = []
        for input in inputs:
            output = skimage.measure.block_reduce(input, (1, 2, 2), np.max)
            outputs.append(output)
        outputs = np.array(outputs)
        cache = (inputs, outputs)
        return outputs, cache

    def backward(self, gradients_for_outputs, cache):
        """
        :param gradients_for_outputs: (N, height/2, width/2, depth)
        :param cache: (inputs, outputs)
        :return: (gradients_for_inputs, gradients_for_parameters)
            gradients_for_inputs: (N, height, width, depth)
            gradients_for_parameters: []
        """
        # (N, depth, height/2, width/2)
        gradients_for_outputs = gradients_for_outputs.transpose((0, 3, 1, 2))

        inputs, outputs = cache
        inputs = inputs.transpose((0, 3, 1, 2))
        outputs = outputs.transpose((0, 3, 1, 2))

        gradients_for_outputs_repeated = gradients_for_outputs.repeat(2, axis=-1).repeat(2, axis=-2)
        mask_maximum_reached = inputs == outputs.repeat(2, axis=-1).repeat(2, axis=-2)
        gradients_for_inputs = gradients_for_outputs_repeated * mask_maximum_reached
        return gradients_for_inputs, []


class FCLayer:
    def forward(self, inputs, weights, biases):
        """
        :param inputs: (N, height, width, depth)
        :param weights: (C, height*width*depth)
            C --- number classes, C = 10
        :param biases: (C)
        :return: (outputs, cache)
            outputs: (N, C)
            cache: (inputs, weights, biases, outputs)
        """
        N, height, width, depth = inputs.shape
        assert weights.shape == (NUMBER_CLASSES, height * width * depth)
        assert biases.shape == (NUMBER_CLASSES,)

        outputs = []
        for input in inputs:
            input_flatten = input.flatten()
            output = weights @ input_flatten
            outputs.append(output)
        outputs = np.array(outputs)
        cache = (inputs, weights, biases, outputs)
        return outputs, cache

    def backward(self, gradients_for_outputs, cache):
        """
        :param gradients_for_outputs: (N, C)
        :param cache: (inputs, weights, biases, outputs)
        :return: (gradients_for_inputs, gradients_for_parameters)
            gradients_for_inputs: (N, height, width, depth)
            gradients_for_parameters: (gradients_for_weights, gradients_for_biases)
                gradients_for_weights: (C, height*width*depth)
                gradients_for_biases: (C)
        """

        inputs, weights, biases, outputs = cache
        N, height, width, depth = inputs.shape

        gradients_for_inputs = []
        gradients_for_weights = []
        gradients_for_biases = np.zeros(NUMBER_CLASSES)
        for input, output, gradients_for_output in zip(inputs, outputs, gradients_for_outputs):
            input_flatten = input.flatten()
            # gradients_for_input[i] = sum_c(d(L)/d(c) * d(c)/d(input[i]))
            # d(L)/d(c) = gradients_for_output[c]
            # d(c)/d(input[i]) = weights[c][i]
            gradients_for_input = (weights * gradients_for_output.reshape((-1, 1))).sum(axis=0)
            gradients_for_input = gradients_for_input.reshape((height, width, depth))
            gradients_for_inputs.append(gradients_for_input)

            # TODO проверить почему gradients_for_weightsне зависит от input
            # gradients_for_weights[c1][i] = sum_c2(d(L)/d(c2) * d(c2)/d(weight[c1][i])) = d(L)/d(c1) * d(c1)/d(weight[c1][i])
            # c2 = sum_i(weight[c2][i] * input[i]) + b[c2]
            gradients_for_weights += weights * gradients_for_output.reshape((-1, 1))

            # gradients_for_biases[c1] = sum_c2(d(L)/d(c2) * d(c2)/d(c1)) = d(L)/d(c1) * 1
            gradients_for_biases += gradients_for_output
        gradients_for_weights /= N
        gradients_for_biases /= N
        return np.array(gradients_for_inputs)


class SoftmaxLayer:
    def forward(self, inputs):
        """
        :param inputs: (N, C)
        :return: (outputs, cache)
            outputs: (N, C)
            cache: (inputs, outputs)
        """

        outputs = []
        for input in inputs:
            input_exp = np.exp(input)
            output = input_exp / np.sum(input_exp)
            outputs.append(output)
        outputs = np.array(outputs)
        cache = (inputs, outputs)
        return outputs, cache

    def backward(self, gradients_for_outputs, cache):
        """
        :param gradients_for_output: (N, C)
        :param cache: (inputs, outputs)
        :return: (gradients_for_inputs, gradients_for_parameters)
            gradients_for_inputs: (N, C)
            gradients_for_parameters: []
        """
        inputs, outputs = cache
        gradients_for_inputs = []
        for input, output, gradients_for_output in zip(inputs, outputs, gradients_for_outputs):
            input_exp = np.exp(input)
            # (d(output_i) / d(input_j)
            jacobian = -(input_exp.reshape((-1, 1)) @ input_exp.reshape((1, -1))) / (np.sum(input_exp) ** 2) + np.diag(output)
            gradients_for_input = gradients_for_output @ jacobian
            gradients_for_inputs.append(gradients_for_input)
        gradients_for_inputs = np.mean(gradients_for_inputs, axis=0)
        return gradients_for_inputs, []


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

        assert x_train.shape[1:] == (28, 28, 1)
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
            # gradients_for_softmax_outputs = np.mean(gradients_for_softmax_outputs, axis=0)
            gradients_for_softmax_outputs = np.array(gradients_for_softmax_outputs)
            assert gradients_for_softmax_outputs.shape == (len(x_train), NUMBER_CLASSES)

            # backward pass
            gradients_for_outputs = gradients_for_softmax_outputs
            for layer, layout_parameters, cache in reversed(zip(self.layers, caches)):
                gradients_for_inputs, gradients_for_parameters = layer.backward(gradients_for_outputs, cache)
                assert len(layout_parameters) == len(gradients_for_parameters)
                for layout_parameter, gradients_for_parameter in zip(layout_parameters, gradients_for_parameters):
                    layout_parameter[...] = layout_parameter - GRADIENT_STEP * gradients_for_parameter
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
    # model.train(x_train, y_train)
    model.predict(x_test)

main()
