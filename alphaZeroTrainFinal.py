from alphaZeroMCTS import alphaZeroMCTS
from tttBoard import tttBoard
from deepNeuralNetwork import dnNetwork
import numpy as np

board1DSize = 3
gamesTrain = 5000
brain = dnNetwork(inputSize=2*board1DSize*board1DSize+1,
                  outputSize=board1DSize*board1DSize+1)

def gameOver(board):
    if (board.winner()):
        if(board.winner()==1):
            return 1
        elif(board.winner()==2):
            return 1
        elif(board.winner()==-1):
            return 1
    else:
        return 0

def playGame(brain,TotalGames):
    games = 0
    allStates = []
    allPiLabels = []
    allZ = []
    while games < TotalGames:
        playedMoves = {}
        board = tttBoard(board1DSize)
        nMoves = 0
        #brain.loadModel()
        while len(board.legalMoves()) > 0:
            state = board.getState()
            alphaZeroTTT = alphaZeroMCTS(board,brain)
            pi = alphaZeroTTT.getMCTSMoveProbs()
            playedMoves[state] = pi
            board.makeMove(np.argmax(pi))
            print("pi ", pi)
            print("move ",np.argmax(pi))
            board.display()
            nMoves += 1
            if gameOver(board):
                games += 1
                winner = board.winner()
                if winner == 1:     # O is winner
                    z = 1
                elif winner == -1:  # draw
                    z = 0
                else:               # X is winner
                    assert(winner == 2)
                    z = -1
                break
        ind = 0
        piLabel = np.zeros((nMoves,board1DSize*board1DSize))
        states = np.zeros((nMoves,2*board1DSize*board1DSize+1))
        Z = np.zeros((nMoves))
        for state in playedMoves:
            pi = playedMoves[state]
            #define the training data structure here, 
            #add z to pi to make output vector
            #add states to make input vector
            piLabel[ind] = pi
            states[ind] = np.float32(board.decodeState(state))
            Z[ind] = z
            ind +=1
        allStates.append(states)
        allPiLabels.append(piLabel)
        allZ.append(Z)
    
    allStates = np.concatenate(allStates)
    allPiLabels = np.concatenate(allPiLabels)
    allZ = np.concatenate(allZ)    
    return (allStates, allPiLabels, allZ)
    
(inp,pi,z) = playGame(brain,gamesTrain)
print("inp",inp)
print("pi",pi)
print("z",z)
brain.train(inp,[pi,z])
brain.saveModel()