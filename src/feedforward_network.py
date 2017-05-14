import tensorflow as tf
from sklearn.model_selection import train_test_split
import numpy as np
import time
import random


class Network:

    def __init__(self, params, vowel, logger):

        self.vowel = vowel

        self.logger = logger

        input_size = 240
        output_size = 2

        if vowel in 'ou':
            output_size = 4

        tf.reset_default_graph()

        self.n_input = tf.placeholder(tf.float32, [None, input_size], name='n_input')
        self.n_output = tf.placeholder(tf.float32, [None, output_size])

        self.hidden_neurons = 100
        self.hidden_neurons2 = 10

        self.b_hidden = tf.Variable(tf.random_normal([self.hidden_neurons]), name='b_hidden')
        self.W_hidden = tf.Variable(tf.random_normal(
            [input_size, self.hidden_neurons]), name='W_hidden')
        self.hidden = tf.sigmoid(
            tf.matmul(self.n_input, self.W_hidden) + self.b_hidden)

        self.b_hidden2 = tf.Variable(tf.random_normal([self.hidden_neurons2]), name='b_hidden2')
        self.W_hidden2 = tf.Variable(tf.random_normal(
            [self.hidden_neurons, self.hidden_neurons2]), name='W_hidden2')
        self.hidden2 = tf.sigmoid(
            tf.matmul(self.hidden, self.W_hidden2) + self.b_hidden2)

        self.W_output = tf.Variable(tf.random_normal(
            [self.hidden_neurons2, output_size]), name='W_output')
        self.output = tf.nn.softmax(tf.matmul(self.hidden2, self.W_output), name='output')

        self.cost = tf.reduce_mean(-tf.reduce_sum(self.n_output * tf.log(self.output), reduction_indices=[1]))

        self.optimizer = tf.train.AdamOptimizer()
        self.train = self.optimizer.minimize(self.cost)

        self.init = tf.global_variables_initializer()

        self.saver = tf.train.Saver()

    def run(self, train_x, train_y, valid_x, valid_y, test_x, test_y):

        self.logger.log('\nvowel: ' + self.vowel)

        self.sess = tf.Session()
        self.sess.run(self.init)
        print("training started")

        best_epoch = 0
        best_loss = 100
        last_loss = 0

        losses = []
        vlosses = []
        eepoch = 0

        start_time = time.perf_counter()
        for i in range(50001):
            batch_x, batch_y = self.next_batch(train_x, train_y, 100)
            cvalues = self.sess.run([self.train, self.cost, self.W_hidden, self.b_hidden, self.W_hidden2, self.b_hidden2, self.W_output], feed_dict={self.n_input: batch_x, self.n_output: batch_y})

            # early stopping
            if i % 50 == 0:
                last_loss = cvalues[1]
                losses += [last_loss]

                vcost = self.sess.run(self.cost, feed_dict={self.n_input: valid_x, self.n_output: valid_y})
                vlosses += [vcost]

                if vcost < best_loss:
                    best_epoch = i
                    best_loss = vcost
                    self.saver.save(self.sess, "./session")
                elif i - best_epoch > 5000 and eepoch == 0:
                    print('early stopping')
                    self.saver.restore(self.sess, "./session")
                    eepoch = best_epoch
                    break

            if i % 10000 == 0:
                print("")
                print("step: {:>3}".format(i))
                print("loss: {}".format(cvalues[1]))
            elif i % 50 == 0:
                print('|', end="")

            last_loss = cvalues[1]

        print("")
        print("elapsed time: " + self.convert_time(time.perf_counter() - start_time))
        print("best loss: " + str(best_loss))

        result = self.sess.run(self.output, feed_dict={self.n_input: test_x})

    def get_model(self):
        return self.sess

    def save_model(self, path):
        self.saver.save(self.sess, path)

    @staticmethod
    def get_random_parameters():
        params = {}
        params['hidden_neurons'] = random.randrange(10, 1000, 10)
        params['hidden_neurons2'] = random.randrange(10, 1000, 10)
        return params

    @staticmethod
    def log_parameters(l, params):
        l.log('\n\nhidden_neurons: ' + str(params['hidden_neurons']))
        l.log('\n\nhidden_neurons2: ' + str(params['hidden_neurons2']))
        pass

    def next_batch(self, data_x, data_y, count):
        batch_x, batch_y = [], []
        indexes = random.sample(range(len(data_x)), count)
        
        for i in indexes:
            batch_x.append(data_x[i])
            batch_y.append(data_y[i])
            
        return batch_x, batch_y

    def convert_time(self, time):
        m, s = divmod(time, 60)
        s, ms = divmod(s, 1)

        return "%02d:%02d:%04d" % (m, s, ms * 1000)