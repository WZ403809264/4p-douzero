# -*- coding: utf-8 -*-
# 将 PyTorch .ckpt 权重导出为 C++ 可加载的自描述二进制格式（.bin）
#
# 文件格式（小端）：
#   int32  tensor 数量 N
#   重复 N 次：
#     int32 名称长度 L
#     char  名称（UTF-8，L 字节）
#     int32 维数 D
#     int32×D 各维大小
#     float32 张量数据（按行主序）
#
# 用法：python export_weights.py [ckpt目录] [输出目录]

import os
import struct
import sys
import torch
from douzero.dmc.models import model_dict

POSITIONS = ['landlord', 'landlord_down1', 'landlord_down2', 'landlord_down3']

def export(position, ckpt_dir, out_dir):
    model = model_dict[position]()
    state = model.state_dict()
    ckpt_path = os.path.join(ckpt_dir, position + '.ckpt')
    pretrained = torch.load(ckpt_path, map_location='cpu')
    pretrained = {k: v for k, v in pretrained.items() if k in state}  # 与 deep.py _load_model 一致
    state.update(pretrained)
    model.load_state_dict(state)
    model.eval()

    sd = model.state_dict()
    out_path = os.path.join(out_dir, position + '.bin')
    with open(out_path, 'wb') as f:
        names = list(sd.keys())
        f.write(struct.pack('<i', len(names)))
        for name in names:
            t = sd[name].detach().cpu().contiguous().float()
            nb = name.encode('utf-8')
            f.write(struct.pack('<i', len(nb)))
            f.write(nb)
            f.write(struct.pack('<i', t.dim()))
            for d in t.shape:
                f.write(struct.pack('<i', int(d)))
            f.write(t.numpy().tobytes())
    print('exported:', out_path)

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    here += r'\baselines\douzero_WP'
    ckpt_dir = sys.argv[1] if len(sys.argv) > 1 else here
    out_dir = sys.argv[2] if len(sys.argv) > 2 else here
    for pos in POSITIONS:
        export(pos, ckpt_dir, out_dir)

if __name__ == '__main__':
    main()
