import numpy as np
import tensorflow as tf
from tensorflow.python.framework import ops


class dNNTF():
    """class for deep Neural Network using Tensorflow
    """
    def __init__(self,board1DSize,*args,**kwds):
        self._saveFile = kwds.get('saveFile')
        self._inputSize = 2*board1DSize*board1DSize+1
        self._outPiSize= board1DSize*board1DSize
        self._parameters = self.initializeParameters()
    def createPlaceholders(self):
        x = tf.placeholder(tf.float64,shape=(self._inputSize,None),name="x")
        yPi = tf.placeholder(tf.float64,shape=(self._outPiSize,None),name="yPi")
        yZ = tf.placeholder(tf.float64,shape=(1,None),name="yZ")
        return x,yPi,yZ
    
    def initializeParameters(self):
        """Initializes parameters to build a neural network with tensorflow. The shapes are:    
           Returns:
        parameters -- a dictionary of tensors containing W1, b1, W2, b2, W3, b3
        """
        w1 = tf.get_variable("w1",[32,self._inputSize],initializer=tf.contrib.layers.xavier_initializer())
        b1 = tf.get_variable("b1",[32,1],initializer=tf.zeros_initializer())
        w2 = tf.get_variable("w2",[16,32],initializer=tf.contrib.layers.xavier_initializer())
        b2 = tf.get_variable("b2",[16,1],initializer=tf.zeros_initializer())
        wPi = tf.get_variable("wPi",[self._outPiSize,16],initializer=tf.contrib.layers.xavier_initializer())
        bPi = tf.get_variable("bPi",[self._outPiSize,1],initializer=tf.zeros_initializer())
        wZ = tf.get_variable("wZ",[1,16],initializer=tf.contrib.layers.xavier_initializer())
        bZ = tf.get_variable("bZ",[1,16],initializer=tf.zeros_initializer())
        parameters = {"w1":w1,"b1":b1,"w2":w2,"b2":b2,"wPi":wPi,"bPi":bPi,"wZ":wZ,"bZ":bZ}
        return parameters
    
    def fwdProp(self,x,parameters):
        """Performs fwd prop LINEAR->RELU->LINEAR->RELU
        Then for Pi layer LINEAR-> SOFTMAX
        For Z layer LINEAR->TANH
        """
        # Retrieve the parameters from the dictionary "parameters" 
        w1 = parameters['w1']
        b1 = parameters['b1']
        w2 = parameters['w2']
        b2 = parameters['b2']
        wPi = parameters['wPi']
        bPi = parameters['bPi']
        wZ = parameters['wZ']
        bZ = parameters['bZ']
        
        z1 = tf.add(tf.matmul(w1,x),b1)
        a1 = tf.nn.relu(z1)
        z2 = tf.add(tf.matmul(w2,a1),b2)
        a2 = tf.nn.relu(z2)
        zPi = tf.add(tf.matmul(wPi,a2),bPi)
        aPi = tf.nn.softmax(zPi)
        zZ = tf.add(tf.matmul(wZ,a2),bZ)
        aZ = tf.nn.tanh(zZ)
        
        return aPi,aZ
    
    def computeCost(self,aPi,aZ,yPi,yZ):
        cost = tf.reduce_mean( tf.square(aZ-yZ) - tf.matmul(tf.transpose(yPi),tf.log(aPi)) )
        return cost
    
    def modelTrain(self,trainX,trainYPi,trainYZ, lr = 0.0001, numEpochs = 1500, printCost=True):
        ops.reset_default_graph()
        costs = []
        (_,m) = trainX.shape
        x,yPi,yZ = self.createPlaceholders()
        parameters = self.initializeParameters()
        aPi,aZ = self.fwdProp(x,parameters)
        cost = self.computeCost(aPi,aZ,yPi,yZ)
        optimizer = tf.train.AdamOptimizer(learning_rate=lr, beta_1=0.99, beta_2=0.999, epsilon=1e-10).minimize(cost)
        
        #initialize all variables
        init = tf.global_variables_initializer()
        
        #start session to compute tensorflow graph
        with tf.Session() as sess:
            #Run initialization
            sess.run(init)
            
            #Do training loop
            for epoch in range(numEpochs):
                epochCost = 0. #Defines cost related to an epoch
                _, c = sess.run([optimizer,cost],feed_dict={x:trainX,yPi:trainYPi,yZ:trainYZ})
                epochCost += c
                if printCost and epoch % 100 == 0:
                    print("Cost after %i:%f" % (epoch,epochCost))
                if printCost and epoch % 5 == 0:
                    costs.append(epochCost)
            
            self._parameters = sess.run(parameters)
            
    
    def predict(self,x):
        p,v = self.fwdProp(x,self._parameters)
        return p,v
                    
                