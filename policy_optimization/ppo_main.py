import tensorflow as tf
from ppo import PPOIQN
import gym
import numpy as np

sess = tf.Session()
PPO = PPOIQN(sess)
sess.run(tf.global_variables_initializer())
env = gym.make('CartPole-v1')
sess.run(PPO.assign_ops)
print(PPO.choose_action([1,2,3,4]))

for episodes in range(1000):
    observations = []
    actions = []
    v_preds = []
    rewards = []
    done = False
    state = env.reset()
    global_step = 0
    while not done:
        global_step += 1
        action, value = PPO.choose_action(state)
        next_state, reward, done, _ = env.step(action)

        observations.append(state)
        actions.append(action)
        v_preds.append(value)
        rewards.append(reward)

        if done:
            v_preds_next = v_preds[1:] + [0]
            reward = -1
        else:
            state = next_state

    gaes = PPO.get_gaes(rewards, v_preds, v_preds_next)
    observations = np.reshape(observations, [-1, PPO.state_size])
    actions = np.array(actions).astype(dtype=np.int32)
    rewards = np.array(rewards).astype(dtype=np.float32)
    v_preds_next = np.array(v_preds_next).astype(dtype=np.float32)
    gaes = np.array(gaes).astype(dtype=np.float32)
    #gaes = (gaes - gaes.mean()) / gaes.std()

    sess.run(PPO.assign_ops)
    inp = [observations, actions, rewards, v_preds_next, gaes]
    for epoch in range(4):
        sample_indices = np.random.randint(low=0, high=observations.shape[0], size=64)  # indices are in [low, high)
        sampled_inp = [np.take(a=a, indices=sample_indices, axis=0) for a in inp]  # sample training data
        PPO.train(obs=sampled_inp[0],
                  actions=sampled_inp[1],
                  rewards=sampled_inp[2],
                  v_preds_next=sampled_inp[3],
                  gaes=sampled_inp[4])
    print(episodes, global_step)