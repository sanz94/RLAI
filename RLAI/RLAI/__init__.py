from gym.envs.registration import register

register(
    id='rlai-v002',
    entry_point='RLAI.envs.rlai_env:rlaiEnv_temp',
)
