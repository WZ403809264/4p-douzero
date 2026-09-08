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
    # 其他玩家出牌
    other_played_cards_env = []
    # 其他玩家手牌（整副牌减去玩家手牌，后续再减掉历史出牌）
    other_hand_cards = []
    # 开局时四个玩家的手牌
    card_play_data_list = {}
    # 八张底牌
    three_landlord_cards_env = []
    # 出牌顺序：0-玩家出牌，1-玩家下家出牌，2-玩家下下家出牌，3-玩家下下下家出牌
    play_order = 0
    # 识别玩家手牌
    user_hand_cards_env = [RealCard2EnvCard[c] for c in list(user_hand_cards_real)]
    # 识别八张底牌
    three_landlord_cards_env = [RealCard2EnvCard[c] for c in list(three_landlord_cards_real)]
    # 识别玩家的角色
    user_position = ['landlord', 'landlord_down1',  'landlord_down2', 'landlord_down3'][user_position_code]
    # 整副牌减去玩家手上的牌，就是其他人的手牌，再分配给另外三个角色（如何分配对AI判断没有影响）
    for i in set(AllEnvCard):
        other_hand_cards.extend([i] * (AllEnvCard.count(i) - user_hand_cards_env.count(i)))
    if user_position_code == 0:
        card_play_data_list.update({
            'three_landlord_cards': three_landlord_cards_env,
            'landlord': user_hand_cards_env,
            'landlord_down1': other_hand_cards[0:25],
            'landlord_down2': other_hand_cards[25:50],
            'landlord_down3': other_hand_cards[50:75]})
    elif user_position_code == 1:
        card_play_data_list.update({
            'three_landlord_cards': three_landlord_cards_env,
            'landlord': other_hand_cards[0:33],
            'landlord_down1': user_hand_cards_env,
            'landlord_down2': other_hand_cards[33:58],
            'landlord_down3': other_hand_cards[58:83]})
    elif user_position_code == 2:
        card_play_data_list.update({
            'three_landlord_cards': three_landlord_cards_env,
            'landlord': other_hand_cards[0:33],
            'landlord_down1': other_hand_cards[33:58],
            'landlord_down2': user_hand_cards_env,
            'landlord_down3': other_hand_cards[58:83]})
    elif user_position_code == 3:
        card_play_data_list.update({
            'three_landlord_cards': three_landlord_cards_env,
            'landlord': other_hand_cards[0:33],
            'landlord_down1': other_hand_cards[33:58],
            'landlord_down2': other_hand_cards[58:83],
            'landlord_down3': user_hand_cards_env})
    # 得到出牌顺序
    play_order = 0 if user_position == "landlord" else 3 if user_position == "landlord_down1" else 2 if user_position == "landlord_down2" else 1
    # 创建一个代表玩家的AI
    ai_players = {}
    ai_players[user_position] = DeepAgent(user_position, card_play_model_path_dict[user_position])
    env = GameEnv(ai_players)
    env.card_play_init(card_play_data_list)
    while not env.game_over:
        # 玩家出牌时就通过智能体获取action，否则通过识别获取其他玩家出牌
        if play_order == 0:
            action_message, win_rate = env.step()
            print(action_message[::-1] if action_message else "P", str(round(float(win_rate) * 100, 2)) + "%")
            play_order = 1
        elif play_order == 1:
            other_played_cards_real = input()
            if(other_played_cards_real == 'P'):
                other_played_cards_real = ''
            other_played_cards_env = [RealCard2EnvCard[c] for c in list(other_played_cards_real)]
            env.other_step(other_played_cards_env)
            play_order = 2
        elif play_order == 2:
            other_played_cards_real = input()
            if(other_played_cards_real == 'P'):
                other_played_cards_real = ''
            other_played_cards_env = [RealCard2EnvCard[c] for c in list(other_played_cards_real)]
            env.other_step(other_played_cards_env)
            play_order = 3
        elif play_order == 3:
            other_played_cards_real = input()
            if(other_played_cards_real == 'P'):
                other_played_cards_real = ''
            other_played_cards_env = [RealCard2EnvCard[c] for c in list(other_played_cards_real)]
            env.other_step(other_played_cards_env)
            play_order = 0
    env.reset()
my_cards, landlords_cards, location = input().split(' ')
init_cards(my_cards, landlords_cards, int(location))