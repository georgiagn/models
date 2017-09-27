# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

import mnist

tf.logging.set_verbosity(tf.logging.ERROR)


class ClassifierBenchmark(tf.test.Benchmark):
  def benchmarkFit(self):
    train_data = np.asarray(np.random.uniform(size=(1000, 784)), dtype=np.float32)
    train_labels = np.asarray(np.random.uniform(size=(1000), high=9), dtype=np.int32)
    classifier = tf.estimator.Estimator(model_fn=mnist.mnist_model_fn, model_dir='')
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
      {'images': train_data}, y=train_labels,
      batch_size=100, num_epochs=None, shuffle=True)
    start = time.time()
    classifier.train(input_fn=train_input_fn, steps=1)
    wall_time = time.time() - start
    self.report_benchmark(name="classifier", wall_time=wall_time)

class BaseTest(tf.test.TestCase):
  def input_fn(self):
    features = tf.random_uniform([55000, 784])
    labels = tf.random_uniform([55000], maxval=9, dtype=tf.int32)
    return features, tf.one_hot(labels, 10)

  def mnist_model_fn_helper(self, mode):
    features, labels = self.input_fn()
    image_count = features.shape[0]
    spec = mnist.mnist_model_fn(features, labels, mode)

    predictions = spec.predictions
    self.assertAllEqual(predictions['probabilities'].shape, (image_count, 10))
    self.assertEqual(predictions['probabilities'].dtype, tf.float32)
    self.assertAllEqual(predictions['classes'].shape, (image_count,))
    self.assertEqual(predictions['classes'].dtype, tf.int64)

    if mode != tf.estimator.ModeKeys.PREDICT:
      loss = spec.loss
      self.assertAllEqual(loss.shape, ())
      self.assertEqual(loss.dtype, tf.float32)

    if mode == tf.estimator.ModeKeys.EVAL:
      eval_metric_ops = spec.eval_metric_ops
      self.assertAllEqual(eval_metric_ops['accuracy'][0].shape, ())
      self.assertAllEqual(eval_metric_ops['accuracy'][1].shape, ())
      self.assertEqual(eval_metric_ops['accuracy'][0].dtype, tf.float32)
      self.assertEqual(eval_metric_ops['accuracy'][1].dtype, tf.float32)

  def test_mnist_model_fn_train_mode(self):
    self.mnist_model_fn_helper(tf.estimator.ModeKeys.TRAIN)

  def test_mnist_model_fn_eval_mode(self):
    self.mnist_model_fn_helper(tf.estimator.ModeKeys.EVAL)

  def test_mnist_model_fn_predict_mode(self):
    self.mnist_model_fn_helper(tf.estimator.ModeKeys.PREDICT)


if __name__ == '__main__':
  tf.test.main()
