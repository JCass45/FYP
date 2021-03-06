#!/home/support/apps/cports/rhel-6.x86_64/gnu/Python/3.5.2/bin/python3

import os
from argparse import ArgumentParser
from traceback import print_exc
import tensorflow as tf
import keras.backend as K
from keras.backend.tensorflow_backend import set_session
from agent import Agent
import util

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

parser = ArgumentParser()
parser.add_argument('game', help='Select which game to play', type=str, choices=util.get_supported_games())
parser.add_argument('deep_learning_mode', help='The type of Deep Learning to use', type=str, choices=['dqn', 'double', 'duel'])
parser.add_argument('training_steps', default=25000, nargs='?', help='The number of steps to run during a training epoch. Default 25000', type=int)
parser.add_argument('training_epochs', default=20, nargs='?', help='The number of training epochs to run. Default 20', type=int)
parser.add_argument('evaluation_games', default=10, nargs='?', help='The number of games to evaluate on. Default 10', type=int)
parser.add_argument('-t', '--test_run', help='Treat this run as a test run? Use when trying new hyperparams etc', action='store_true')
parser.add_argument('-l', '--load_model', default=True, help='Use this flag to start with a new model', action='store_false')
parser.add_argument('-d', '--display', help='Display video output of game?', action='store_true')
parser.add_argument('-r', '--record', help='Record a simulation of the game?', action='store_true')
args = parser.parse_args()


def main():
    agent = Agent(
        args.game,
        args.deep_learning_mode,
        display=args.display,
        load_model=args.load_model,
        record=args.record,
        test=args.test_run
    )

    if args.record:
        util.record(agent, './data/recordings/{}/{}/'.format(args.game, args.deep_learning_mode))
        return

    games_to_play = args.evaluation_games
    for epoch in range(args.training_epochs):
        try:
            print('Training Epoch: ', epoch + 1)
            print('************************')
            running_score = 0
            frames_survived = 0
            avg_loss = agent.training(args.training_steps)
            for i in range(games_to_play):
                print('Evaluation Game: ', i)
                agent_scores = agent.simulate_intelligent(evaluating=True)
                running_score += agent_scores[0]
                frames_survived += agent_scores[1]
        except:
            print('There was an exception!')
            print('############ Traceback ##############')
            print_exc()
            print('#####################################', end='\n\n')
            print('Quitting...')
            break
        finally:
            running_score /= games_to_play
            frames_survived /= games_to_play
            # Save the Average Score and Frames survived over 10 agents for this interval
            util.save_results(
                './data/{1}/{0}_avgscore_{1}.npy'.format(agent.name, args.deep_learning_mode),
                running_score
            )

            util.save_results(
                './data/{1}/{0}_avgframes_surv_{1}.npy'.format(agent.name, args.deep_learning_mode),
                frames_survived
            )

            # Save the average model loss over each training epoch
            # There are interval / 3 training epochs per interval
            util.save_results(
                './data/{1}/{0}_loss_{1}.npy'.format(agent.name, args.deep_learning_mode),
                avg_loss
            )


def play_and_display_intelligent():
    agent = Agent(
        args.game,
        args.deep_learning_mode,
        display=True,
        load_model=True,
        record=False,
        test=args.test_run
    )
    agent.simulate_intelligent(evaluating=True)


def play_randomly():
    agent = Agent(
        args.game,
        args.deep_learning_mode,
        display=False,
        load_model=False,
        record=False,
        test=args.test_run
    )
    agent.simulate_random()


if __name__ == '__main__':
    # play_and_display_intelligent()
    main()
    K.clear_session()
