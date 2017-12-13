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
        obs += [float(np.random.poisson(z[-1].dot(b)))]

    return obs, z

n = 7
p_true = [.7, .3]
A_true = array([[0.8,0.4],[0.2,0.6]])
b_true = [0.1, 2.]

obs_train, z_train = build_toy_dataset(n, p_true, A_true, b_true)
obs_test, z_test = build_toy_dataset(n, p_true, A_true, b_true)
 
#obs = tf.placeholder(tf.float32, [n])


def gen_hmm(vd):
    z = tf.expand_dims(
        tf.transpose(
        tf.expand_dims(Multinomial(total_count=1., probs=vd['p']), 0)), 0)
    obs = tf.expand_dims(Poisson(rate=tf.matmul(tf.expand_dims(vd['b'],0), z[-1])), 0)
    
    for t in range(n-1):
        z_new = tf.transpose(Multinomial(total_count=1.,
                                probs=tf.transpose(tf.matmul(tf.transpose(vd['A']),z[-1]), 
                                    name='tx_prob')),name='z_new')
         
        z = tf.concat([z,tf.expand_dims(z_new,0)],0)
        obs = tf.concat([obs, 
                         tf.expand_dims(
                         Poisson(rate=tf.matmul(tf.expand_dims(vd['b'],0), z_new)),0)], 0)
    return obs, z
p_p_alpha = [2.,2.]
p_A_alpha = [[2.,1.],[1.,2.]]
p_b_alpha = [0.5,2.0]
p_b_beta =  [1.,1.]

q_p_alpha = tf.Variable(p_p_alpha) 
q_A_alpha = tf.Variable(p_A_alpha)
q_b_alpha = tf.Variable(p_b_alpha)
q_b_beta =  tf.Variable(p_b_beta)

p = Dirichlet(p_p_alpha, name='p')
A = Dirichlet(p_A_alpha, name='A')
b = Gamma(p_b_alpha, p_b_beta)

qp = Dirichlet(q_p_alpha, name='p')
qA = Dirichlet(q_A_alpha, name='A')
qb = Gamma(q_b_alpha, q_b_beta)
    
obs, z = gen_hmm({'p':p, 'A':A, 'b':b})
obs_train, z_train = build_toy_dataset(n, p_true, A_true, b_true)
obs_train = tf.expand_dims(tf.expand_dims(obs_train, 0), 0)

latent_vars = {p: qp, A: qA, b: qb}
data = {tf.squeeze(obs): tf.squeeze(obs_train)}

inference = ed.KLqp(latent_vars, data)
inference.run(n_iter=2500)

print(qp.eval())
print(tf.transpose(qA).eval())
print(qb.eval())

obs_post = ed.copy(obs, {p: qp, A: qA, b: qb})
print("posterior observations")
print(tf.squeeze(obs_post).eval())
print("training observations")
print(tf.squeeze(obs_train).eval())
print("Mean absolute error on training data:")
print(ed.evaluate('mean_absolute_error', data={tf.squeeze(obs_post): tf.squeeze(obs_train)}))
print("test observations")
print(tf.squeeze(obs_test).eval())
print("Mean absolute error on test data:")
print(ed.evaluate('mean_absolute_error', data={tf.squeeze(obs_post): tf.squeeze(obs_test)}))

file_writer = tf.summary.FileWriter('/home/kyjohnso/projects/mlbslice/tb_logs',
                                    tf.get_default_graph()) 

sess.close()
