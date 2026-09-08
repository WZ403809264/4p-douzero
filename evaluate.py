import os 
import argparse

from douzero.evaluation.simulation import evaluate

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    'Dou Dizhu Evaluation')
    parser.add_argument('--landlord', type=str,
            default='baselines/douzero_WP/landlord.ckpt')
    parser.add_argument('--landlord_down1', type=str,
            default='baselines/douzero_WP/landlord_down1.ckpt')
    parser.add_argument('--landlord_down2', type=str,
            default='baselines/douzero_WP/landlord_down2.ckpt')
    parser.add_argument('--landlord_down3', type=str,
            default='baselines/douzero_WP/landlord_down3.ckpt')
    parser.add_argument('--eval_data', type=str,
            default='eval_data.pkl')
    parser.add_argument('--num_workers', type=int, default=5)
    parser.add_argument('--gpu_device', type=str, default='')
    parser.add_argument('--output', action='store_true')
    args = parser.parse_args()

    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_device

    evaluate(args.landlord,
             args.landlord_down1,
             args.landlord_down2,
             args.landlord_down3,
             args.eval_data,
             args.num_workers,
             args.output)
