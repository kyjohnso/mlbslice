#!/usr/bin/env python

import tensorflow as tf
import edward as ed
import numpy as np

from numpy import array
from numpy.linalg import norm
from edward.models import Dirichlet, Multinomial, Gamma, Poisson

sess = tf.Session()

def build_toy_dataset(n, p, A, b):
    """
    toy HMM with: 
        n=number of timesteps,
        p=m length array where m is the number of hidden states and p_i is the 
            initial probability of being in state i
        A=mxm transition matrix indexed by i, j where the (i,j) element is the
            probability of transitioning from element j to element i
        b=m length array where b_i contains the poison rate for state i
    """
    p = array(p)/float(sum(p))
    z = [np.random.multinomial(1, p)]
    obs = [np.random.poisson(z[-1].dot(b))]

    for step in range(n-1):
        z += [np.random.multinomial(1, z[-1].dot(A))]
        obs += [np.random.poisson(z[-1].dot(b))]

    return array(obs), array(z)

n = 7
A_true = array([[0.8,0.4],[0.2,0.6]])
p_true = [.7, .3]
b_true = [2, 10]

obs_train, z_train = build_toy_dataset(30, p_true, A_true, b_true)
obs_test, z_test = build_toy_dataset(30, p_true, A_true, b_true)
 
#obs = tf.placeholder(tf.float32, [n])

A_alpha = [[2.,1.],[1.,2.]] # these alpha parameters for the transition
                            #   dirichlet distribution mean the probability
                            #   of staying in the same state is higher than the                             #   probability of transitioning

A = tf.transpose(Dirichlet(A_alpha))
p = Dirichlet([2.,2.])
b = tf.expand_dims(Gamma([0.5,2.0], [1.,1.]), 0)

z = tf.expand_dims(
    tf.transpose(
    tf.expand_dims(Multinomial(total_count=1., probs=p), 0)), 0)
obs = tf.expand_dims(Poisson(rate=tf.matmul(b, z[-1])), 0)

for t in range(n-1):
    z = tf.concat([z,
                   tf.expand_dims(tf.transpose(
                                    Multinomial(total_count=1.,
                                    probs=tf.transpose(tf.matmul(A,z[-1])))
                                                ),0)],0)

    obs = tf.concat([obs, 
                     tf.expand_dims(Poisson(rate=tf.matmul(b, z[-1])),0)], 0)

print(sess.run(obs))
 

    


