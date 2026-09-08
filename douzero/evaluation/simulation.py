import multiprocessing as mp
import pickle

from douzero.env.game import GameEnv, EnvCard2RealCard


def load_card_play_models(card_play_model_path_dict):
    players = {}

    for position in ['landlord', 'landlord_down1', 'landlord_down2', 'landlord_down3']:
        if card_play_model_path_dict[position] == 'random':
            from .random_agent import RandomAgent
            players[position] = RandomAgent()
        else:
            from .deep_agent import DeepAgent
            players[position] = DeepAgent(position, card_play_model_path_dict[position])
    return players

def mp_simulate(card_play_data_list, card_play_model_path_dict, q):

    players = load_card_play_models(card_play_model_path_dict)

    env = GameEnv(players)
    for idx, card_play_data in enumerate(card_play_data_list):
        env.card_play_init(card_play_data)
        while not env.game_over:
            env.step()
        env.reset()

    q.put((env.num_wins['landlord'],
           env.num_wins['farmer'],
           env.num_scores['landlord'],
           env.num_scores['farmer']
         ))

def mp_simulate_with_output(card_play_data_list, card_play_model_path_dict, q):

    players = load_card_play_models(card_play_model_path_dict)

    env = GameEnv(players)
    for idx, card_play_data in enumerate(card_play_data_list):
        env.card_play_init(card_play_data)
        print()
        print("第" + str(idx + 1) + "轮游戏开始")
        print("landlord手牌：" + str(''.join([EnvCard2RealCard[c] for c in env.info_sets['landlord'].player_hand_cards]))[::-1])
        print("landlord_down1手牌：" + str(''.join([EnvCard2RealCard[c] for c in env.info_sets['landlord_down1'].player_hand_cards]))[::-1])
        print("landlord_down2手牌：" + str(''.join([EnvCard2RealCard[c] for c in env.info_sets['landlord_down2'].player_hand_cards]))[::-1])
        print("landlord_down3手牌：" + str(''.join([EnvCard2RealCard[c] for c in env.info_sets['landlord_down3'].player_hand_cards]))[::-1])
        print("地主牌：" + str(''.join([EnvCard2RealCard[c] for c in env.three_landlord_cards]))[::-1])
        print()
        while not env.game_over:
            position = env.acting_player_position
            action, winrate = env.step()
            if winrate != None:
                print(position + "出牌：" + (action[::-1] if action else "P") + " " + str(round(float(winrate) * 100, 2)) + "%")
            else:
                print(position + "出牌：" + (action[::-1] if action else "P"))
        print()
        print("胜利者：" + env.winner)
        print("第" + str(idx + 1) + "轮游戏结束")
        print()
        env.reset()

    q.put((env.num_wins['landlord'],
           env.num_wins['farmer'],
           env.num_scores['landlord'],
           env.num_scores['farmer']
         ))

def data_allocation_per_worker(card_play_data_list, num_workers):
    card_play_data_list_each_worker = [[] for k in range(num_workers)]
    for idx, data in enumerate(card_play_data_list):
        card_play_data_list_each_worker[idx % num_workers].append(data)

    return card_play_data_list_each_worker

def evaluate(landlord, landlord_down1, landlord_down2, landlord_down3, eval_data, num_workers, output=False):

    if output:
        num_workers = 1

    with open(eval_data, 'rb') as f:
        card_play_data_list = pickle.load(f)

    card_play_data_list_each_worker = data_allocation_per_worker(
        card_play_data_list, num_workers)
    del card_play_data_list

    card_play_model_path_dict = {
        'landlord': landlord,
        'landlord_down1': landlord_down1,
        'landlord_down2': landlord_down2,
        'landlord_down3': landlord_down3}

    num_landlord_wins = 0
    num_farmer_wins = 0
    num_landlord_scores = 0
    num_farmer_scores = 0
    
    ctx = mp.get_context('spawn')
    q = ctx.SimpleQueue()
    processes = []
    for card_play_data in card_play_data_list_each_worker:
        p = ctx.Process(
                target=(mp_simulate_with_output if output else mp_simulate),
                args=(card_play_data, card_play_model_path_dict, q))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    for i in range(num_workers):
        result = q.get()
        num_landlord_wins += result[0]
        num_farmer_wins += result[1]
        num_landlord_scores += result[2]
        num_farmer_scores += result[3]

    num_total_wins = num_landlord_wins + num_farmer_wins
    print('WP results:')
    print('landlord : Farmers - {} : {}'.format(num_landlord_wins / num_total_wins, num_farmer_wins / num_total_wins))
    print('ADP results:')
    print('landlord : Farmers - {} : {}'.format(num_landlord_scores / num_total_wins, 3 * num_farmer_scores / num_total_wins)) 
