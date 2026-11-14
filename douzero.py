from collections import Counter

from douzero.env.game import GameEnv
from douzero.evaluation.deep_agent import DeepAgent
# 模型路径
card_play_model_path_dict = {
    'landlord': "baselines/douzero_WP/landlord.ckpt",
    'landlord_down1': "baselines/douzero_WP/landlord_down1.ckpt",
    'landlord_down2': "baselines/douzero_WP/landlord_down2.ckpt",
    'landlord_down3': "baselines/douzero_WP/landlord_down3.ckpt"
}
RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                    '8': 8, '9': 9, '0': 10, 'J': 11, 'Q': 12,
                    'K': 13, 'A': 14, '2': 17, 'Y': 20, 'Z': 30}
EnvCard2RealCard = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                    8: '8', 9: '9', 10: '0', 11: 'J', 12: 'Q',
                    13: 'K', 14: 'A', 17: '2', 20: 'Y', 30: 'Z'}
AllEnvCard = [3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6,
              7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9,
              10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12,
              13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 17, 17, 17, 17, 17, 17, 17, 17,
              20, 20, 30, 30]
def init_cards(user_hand_cards_real, three_landlord_cards_real, user_position_code):
    # 识别玩家手牌 / 底牌 / 位置
    user_hand_cards_env = [RealCard2EnvCard[c] for c in list(user_hand_cards_real)]
    three_landlord_cards_env = [RealCard2EnvCard[c] for c in list(three_landlord_cards_real)]
    all_positions = ['landlord', 'landlord_down1', 'landlord_down2', 'landlord_down3']
    user_position = all_positions[user_position_code]

    # ===== 并集公式核心状态 =====
    # other_hand_union: 其他三家手牌并集 = 整副牌 − AI 手牌 − 历史所有出牌
    # 用 Counter 维护，每次 other_step 时扣减实际打出的牌，杜绝"删错手牌"。
    other_hand_union = Counter(AllEnvCard)
    other_hand_union.subtract(Counter(user_hand_cards_env))

    # num_left: 每家剩余牌数。AI 自己的由 GameEnv 内部 update_acting_player_hand_cards
    # 正确维护（按值 remove），其他三家的由本函数按"上家牌数 − 这次出牌数"维护。
    num_left = {'landlord': 33, 'landlord_down1': 25,
                'landlord_down2': 25, 'landlord_down3': 25}
    num_left[user_position] = len(user_hand_cards_env)

    # 给 GameEnv.card_play_init 的初始手牌切分（仅用于让 GameEnv 启动；
    # 预测只看并集，单家具体分配不影响 AI 决策）
    other_positions = [p for p in all_positions if p != user_position]
    other_list = sorted(other_hand_union.elements())
    slices = {}
    idx = 0
    for pos in other_positions:
        n = num_left[pos]
        slices[pos] = other_list[idx:idx + n]
        idx += n
    card_play_data_list = {
        'three_landlord_cards': three_landlord_cards_env,
        user_position: user_hand_cards_env,
        **slices,
    }

    ai_players = {user_position: DeepAgent(user_position, card_play_model_path_dict[user_position])}
    env = GameEnv(ai_players)
    env.card_play_init(card_play_data_list)

    # ===== 包装 get_infoset：强制 other_hand_cards / num_cards_left_dict 走并集公式 =====
    # 不论当前 acting_player_position 是谁，覆盖都不会破坏 AI 自己的视角
    # （env.step 内部对 AI 视角调用本方法时，other_hand_cards 即为正确并集）。
    original_get_infoset = env.get_infoset
    def get_infoset_with_union():
        info = original_get_infoset()
        info.other_hand_cards = sorted(other_hand_union.elements())
        info.num_cards_left_dict = dict(num_left)
        return info
    env.get_infoset = get_infoset_with_union

    # ===== 手动实现 other_step，不依赖 GameEnv 内部可能错误/缺失的同名方法 =====
    # 原 GameEnv 没有 other_step，且历史版本曾用 del 前 N 张删错手牌；
    # 这里在 env 实例上绑定正确实现：推进状态 + 按值扣减并集公式状态。
    def other_step(action):
        if len(action) > 0:
            env.last_pid = env.acting_player_position
        env.last_move_dict[env.acting_player_position] = action.copy()
        env.card_play_action_seq.append(action)
        env.played_cards[env.acting_player_position] += action
        for card in action:
            other_hand_union[card] -= 1
        num_left[env.acting_player_position] -= len(action)
        env.game_done()
        if not env.game_over:
            env.get_acting_player_position()
            env.game_infoset = env.get_infoset()
    env.other_step = other_step

    # 出牌顺序：0=AI 出牌, 1/2/3=其他三家依次
    play_order = 0 if user_position == "landlord" \
                 else 3 if user_position == "landlord_down1" \
                 else 2 if user_position == "landlord_down2" \
                 else 1

    while not env.game_over:
        if play_order == 0:
            action_message, win_rate = env.step()
            print(action_message[::-1] if action_message else "P",
                  str(round(float(win_rate) * 100, 2)) + "%")
        else:
            other_played_cards_real = input()
            if other_played_cards_real == 'P':
                other_played_cards_real = ''
            other_played_cards_env = [RealCard2EnvCard[c] for c in list(other_played_cards_real)]
            env.other_step(other_played_cards_env)
        play_order = (play_order + 1) % 4

    env.reset()
my_cards, landlords_cards, location = input().split(' ')
init_cards(my_cards, landlords_cards, int(location))