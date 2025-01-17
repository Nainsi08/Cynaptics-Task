# -*- coding: utf-8 -*-
"""subtask2 (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sWt3wKV-UpzoXaovLvLPjr3kVbTamaNh
"""

!unzip archive.zip

import os
import numpy as np
from numpy import array
import PIL
from tensorflow.keras import layers
import cv2
import time
from numpy import savez_compressed
from numpy import load
from numpy import expand_dims
from numpy import zeros
from numpy import ones
from numpy.random import randn
from numpy import vstack
from tensorflow.keras.datasets.cifar10 import load_data
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Reshape
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Conv2DTranspose
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.layers import Dropout
from numpy.random import randint
from keras.datasets.mnist import load_data
import matplotlib.pyplot as plt
import tensorflow as tf
import glob
import imageio
from IPython import display

print ("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
if tf.test.gpu_device_name():
  print('Default GPU Device:'.format(tf.test.gpu_device_name()))
else:
  print("Please install GPU version of TF")

# Adding our data to a numpy array
st = time.time()
cwdInput = "/content/images/*.jpg"
img_input_dir = cwdInput
files = glob.glob(img_input_dir)
print (len(files))

X_data = []
iterations = 0
target_size = (128, 128)  # Specify your desired target size

for myFile in files:
      image = cv2.imread (myFile)
      # Resize the image before appending
      image = cv2.resize(image, target_size)
      X_data.append (image)
      iterations = iterations+1
      if(iterations % 1000 == 0):
         print(iterations)
      if(iterations ==36000):
        break


X_data_array = np.asarray(X_data)
print ('X_data shape:' , X_data_array.shape)
print ("The program took %s seconds :" %(time.time()-st))

# save as compressed numpy array
filename = 'archive'
savez_compressed(filename, X_data_array)
print(' Saved dataset: ', filename)

data = np.load('archive.npz')
print(data['arr_0'])

# data = np.load('archive.npz')
print("Arrays in the file:", data.files)

train_Images = data['arr_0']
print("Shape of the array:", train_Images.shape)

if len(train_Images.shape) >= 3:
    n_samples = min(3, train_Images.shape[0])

    plt.figure(figsize=(15, 5))
    for i in range(n_samples):
        plt.subplot(1, n_samples, i + 1)
        plt.axis('off')


        img = train_Images[i]
        if img.dtype != np.uint8:
            img = (img * 255).astype(np.uint8)  # Normalize if needed

        plt.imshow(img)
        plt.title(f'Image {i+1}')

    plt.tight_layout()
    plt.show()
else:
    print("The array doesn't seem to contain image data. Shape:", train_Images.shape)

print(len(train_Images))

def make_discriminator(in_shape=(128, 128, 3)):
    model = Sequential()

    # First layer
    model.add(Conv2D(64, (3,3), padding='same', input_shape=in_shape))
    model.add(LeakyReLU(alpha=0.2))

    # Second layer
    model.add(Conv2D(128, (3,3), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    # Third layer
    model.add(Conv2D(256, (3,3), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    # Fourth layer
    model.add(Conv2D(512, (3,3), strides=(2,2), padding='same'))
    model.add(LeakyReLU(alpha=0.2))

    # Flatten layer
    model.add(Flatten())
    model.add(Dropout(0.4))

    # Output layer
    model.add(Dense(1, activation='sigmoid'))

    # Compile model
    opt = Adam(learning_rate=0.0002, beta_1=0.5)
    model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])

    return model

def make_generator(latent_dim):
   model = Sequential()

   # Initial dense layer
   n_nodes = 8 * 8 * 512
   model.add(Dense(n_nodes, input_dim=latent_dim))
   model.add(LeakyReLU(alpha=0.2))
   model.add(Reshape((8, 8, 512)))  # Fixed reshape dimensions

   # First upsampling block
   model.add(Conv2DTranspose(256, (4,4), strides=(2,2), padding='same'))
   model.add(LeakyReLU(alpha=0.2))

   # Second upsampling block
   model.add(Conv2DTranspose(128, (4,4), strides=(2,2), padding='same'))
   model.add(LeakyReLU(alpha=0.2))

   # Third upsampling block
   model.add(Conv2DTranspose(64, (4,4), strides=(2,2), padding='same'))
   model.add(LeakyReLU(alpha=0.2))

   # Fourth upsampling block
   model.add(Conv2DTranspose(32, (4,4), strides=(2,2), padding='same'))
   model.add(LeakyReLU(alpha=0.2))

   # Output layer
   model.add(Conv2D(3, (3,3), activation='tanh', padding='same'))

   return model

def add_to_gan(g_model, d_model):
    d_model.trainable = False
    model = Sequential()
    model.add(g_model)
    model.add(d_model)
    opt = Adam(lr=0.0002, beta_1=0.5)
    return model

def load_real_samples():
    X = datal ['arr_0']
    # convert fron unsigned ints to floats
    x = X.astype('float32')
    #scale from [0,255] to [-1,1]
    x = (x - 127.5) / 127.5
    return x

def generate_real_samples(dataset, n_samples):
    ix = randint (0, dataset.shape[0], n_samples)
    X = dataset [ix]
    y = ones((n_Samples, 1))
    return X, y

def generate_latent_points(latent_dim, n_samples):
    x_input = randn(latent_dim * n_samples)
    x_input = x_input.reshape(n_samples, latent_dim)
    return x_input

def generate_fake_samples(g_model, latent_dim, n_samples):
    X_input = generate_latent_points(latent_dim, n_samples)
    X = g_model.predict(x_input)
    y = zeros( (n_samples, 1))
    return X, y

# create and save a plot of generated images
def save_plot(examples, epoch, n=4):
    # scale from [-1,1] to [0,1]
    examples = (examples + 1) / 2.0
    # plot images
    for i in range(n * n):
           # define subplot
           plt. subplot(n, n, 1 + i)
           # turn off axis
           pit.axis('off')
           # plot raw pixel data
           plt.imshow(examples [i])
    #save plot to file
    filename = 'generated_data/generated_plot_e%03d.png' % (epoch+1)
    plt. savefig(filename)
    pit.close()

def summarize_performance(epoch, g_model, d_model, dataset, latent_dim, n_samples=150):
    X_real, y_real = generate_real_samples(dataset, n_samples)
    _, per_real = d_model.evaluate(X_real, y_real, Verbose=0)
    x_fake, y_fake = generate_fake_samples(g_model, latent_dim, n_samples)
    _, per_fake = d_model.evaluate(x_fake, y_fake, verbose=0)
    print('>Accuracy real: %.0f%%, fake: %.0f%%' % (per_real*100, per_fake*100))
    save_plot(x_fake, epoch)
    filename = ('generated_data/generator_model_%03d.hS') % (epoch+1)
    g_model.save(filename)

def train(g_model, d_model, gan_model, dataset, latent_dim, n_epochs=200, n_batch=120):
    bat_per_epo = int(dataset.shape[0] / n_batch)
    half_batch = int(n_batch / 2)
    for i in range(n_epochs):
       for j in range(bat_per_epo):
               X_real, y_real = generate_real_samples(dataset, half_batch)
       d_loss1, _ = d_model.train_on_batch(X_real, y_real)
       X_fake,y_fake = generate_fake_samples(g_model, latent_dim, half_batch)
       d_loss2, _ = d_model.train_on_batch(X_fake, У_fake)
       X_gan = generate_latent_points (latent_dim, n_batch)
       Y_ean = ones((a_batch, 1))
       g_loss = gan_model. train_on_batch(X_gan, y_gan)
       print('›%d, %d/%d, d1=%.3f, d2=%.3f g=%.3f' %
             (i+1, j+1, bat_per_epo, d_loss1, d_loss2, g_loss))
    if (i+1) % 10 == 0:
             summarize_performance(i, g_model, d_model, dataset, latent_dim)

def add_to_gan(generator, discriminator):
    # Freeze discriminator weights while training the generator
    discriminator.trainable = False

    # Create the GAN model
    from keras.models import Model
    from keras.layers import Input

    gan_input = Input(shape=(generator.input_shape[1],))
    gan_output = discriminator(generator(gan_input))
    gan_model = Model(gan_input, gan_output)

    # Compile the GAN model
    gan_model.compile(optimizer=Adam(learning_rate=0.0002, beta_1=0.5), loss='binary_crossentropy')

    return gan_model

# Ensure all necessary imports
from keras.models import Sequential
from keras.optimizers import Adam
from numpy.random import randn
from numpy import load

# Load dataset
dataset = train_Images

# Normalize dataset
dataset = (dataset.astype('float32') - 127.5) / 127.5

# Initialize models
latent_dim = 100
d_model = make_discriminator()
g_model = make_generator(latent_dim)
gan_model = add_to_gan(g_model, d_model)

# Train the GAN
train(g_model, d_model, gan_model, dataset, latent_dim)