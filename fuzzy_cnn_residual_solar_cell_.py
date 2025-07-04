# -*- coding: utf-8 -*-
"""Fuzzy CNN residual Solar cell .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yQG-8D87vI_s-nQc38O6bRuMqrejchXe
"""

import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dropout, Dense, Layer, Add
from tensorflow.keras.models import Model

class FuzzyInferenceBlock(Layer):
    def __init__(self, output_dim, **kwargs):
        self.output_dim = output_dim
        super(FuzzyInferenceBlock, self).__init__(**kwargs)

    def build(self, input_shape):
        super(FuzzyInferenceBlock, self).build(input_shape)

    def call(self, inputs):

        mu = tf.reduce_mean(inputs, axis=[0, 1, 2])
        sigma = tf.math.reduce_std(inputs, axis=[0, 1, 2])

        input_shape = tf.shape(inputs)
        mu_map = tf.ones((self.output_dim, input_shape[-1])) * tf.expand_dims(mu, axis=0)
        sigma_map = tf.ones((self.output_dim, input_shape[-1])) * tf.expand_dims(sigma, axis=0)

        aligned_x = tf.expand_dims(inputs, axis=-1)
        aligned_c = tf.expand_dims(mu_map, axis=-2)
        aligned_s = tf.expand_dims(sigma_map, axis=-2)

        phi = tf.exp(-tf.reduce_sum(tf.square(aligned_x - aligned_c) / (2 * tf.square(aligned_s)), axis=-1))
        return phi

def fcnn_with_residual_attention(n_femap=4, stride=2, dropout=True):
    rows, cols = 224, 224
    inp = Input(shape=[rows, cols, 3])

    conv1 = Conv2D(16, (7, 7), padding='valid', strides=(3, 3), activation='relu')(inp)
    conv1 = MaxPooling2D((3, 3), strides=(1, 1), padding='same')(conv1)

    conv2 = Conv2D(32, (3, 3), padding='same', strides=(2, 2), activation='relu')(conv1)
    conv2 = MaxPooling2D((2, 2), strides=(1, 1), padding='same')(conv2)

    conv3 = Conv2D(32, (3, 3), padding='same', strides=(2, 2), activation='relu')(conv2)
    conv3 = MaxPooling2D((2, 2), strides=(1, 1), padding='same')(conv3)

    conv4 = Conv2D(32, (3, 3), padding='same', strides=(2, 2), activation='relu')(conv3)
    conv4 = MaxPooling2D((2, 2), strides=(1, 1), padding='same')(conv4)

    conv5 = Conv2D(n_femap, (4, 4), padding='same', strides=(stride, stride), activation='relu')(conv4)
    if dropout:
        conv5 = Dropout(0.2)(conv5)

    fuzzy_inference = []
    for i in range(n_femap):
        f_block = FuzzyInferenceBlock(output_dim=1)(conv5)
        fuzzy_inference.append(f_block)

    fuzzy_inference_res = Add()(fuzzy_inference)

    flatten_layer = Flatten()(fuzzy_inference_res)
    out = Dense(3, activation='softmax')(flatten_layer)

    model = Model(inp, out)
    return model

# Create the model
FCNRA = fcnn_with_residual_attention(n_femap=128)

# Compile the model with Binary Cross-Entropy loss
FCNRA .compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Display model summary
FCNRA .summary()