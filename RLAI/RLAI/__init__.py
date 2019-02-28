from gym.envs.registration import register

register(
    id='rlai-v001',
    entry_point='RLAI.envs.rlai_env:rlaiEnv',
)