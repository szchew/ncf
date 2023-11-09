import pandas as pd
import numpy as np
from gmf import GMFEngine
from mlp import MLPEngine
from neumf import NeuMFEngine
from data import SampleGenerator

gmf_config = {
    "alias": "gmf_factor8neg4-implict",
    "num_epoch": 200,
    "batch_size": 1024,
    # 'optimizer': 'sgd',
    # 'sgd_lr': 1e-3,
    # 'sgd_momentum': 0.9,
    # 'optimizer': 'rmsprop',
    # 'rmsprop_lr': 1e-3,
    # 'rmsprop_alpha': 0.99,
    # 'rmsprop_momentum': 0,
    "optimizer": "adam",
    "adam_lr": 1e-3,
    "num_users": 6040,
    "num_items": 3706,
    "latent_dim": 8,
    "num_negative": 4,
    "l2_regularization": 0,  # 0.01
    "use_cuda": True,
    "device_id": 0,
    "model_dir": "checkpoints/{}_Epoch{}_HR{:.4f}_NDCG{:.4f}.model",
}

mlp_config = {
    "alias": "mlp_factor8neg4_bz256_166432168_pretrain_reg_0.0000001",
    "num_epoch": 200,
    "batch_size": 256,  # 1024,
    "optimizer": "adam",
    "adam_lr": 1e-3,
    "num_users": 6040,
    "num_items": 3706,
    "latent_dim": 8,
    "num_negative": 4,
    "layers": [
        16,
        64,
        32,
        16,
        8,
    ],  # layers[0] is the concat of latent user vector & latent item vector
    "l2_regularization": 0.0000001,  # MLP model is sensitive to hyper params
    "use_cuda": True,
    "device_id": 7,
    "pretrain": True,
    "pretrain_mf": "checkpoints/{}".format(
        "gmf_factor8neg4_Epoch100_HR0.6391_NDCG0.2852.model"
    ),
    "model_dir": "checkpoints/{}_Epoch{}_HR{:.4f}_NDCG{:.4f}.model",
}

neumf_config = {
    "alias": "pretrain_neumf_factor8neg4",
    "num_epoch": 200,
    "batch_size": 1024,
    "optimizer": "adam",
    "adam_lr": 1e-3,
    "num_users": 6040,
    "num_items": 3706,
    "latent_dim_mf": 8,
    "latent_dim_mlp": 8,
    "latent_dim_cnn": 8,
    "num_negative": 4,
    "layers": [
        16,
        32,
        16,
        8,
    ],  # layers[0] is the concat of latent user vector & latent item vector
    "cnn_layers": [
        16,
        32,
        16,
        8,
    ],  # layers[0] is the concat of latent user vector & latent item vector
    "l2_regularization": 0.01,
    "use_cuda": True,
    "device_id": 7,
    "pretrain": True,
    "pretrain_mf": "checkpoints/{}".format(
        "gmf_factor8neg4_Epoch100_HR0.6391_NDCG0.2852.model"
    ),
    "pretrain_mlp": "checkpoints/{}".format(
        "mlp_factor8neg4_Epoch100_HR0.5606_NDCG0.2463.model"
    ),
    "model_dir": "checkpoints/{}_Epoch{}_HR{:.4f}_NDCG{:.4f}.model",
}

# Load Data
data_dir = "./data/combined_data_1.txt"
data = []

with open(data_dir, "r") as file:
    movie_id = None
    for line in file:
        line = line.strip()
        if line.endswith(":"):
            movie_id = int(line[:-1])
        else:
            customer_id, rating, date = line.split(",")
            data.append([movie_id, int(customer_id), int(rating), date])

data = pd.DataFrame(data, columns=["itemId", "userId", "rating", "timestamp"])

print("Range of userId is [{}, {}]".format(data.userId.min(), data.userId.max()))
print("Range of itemId is [{}, {}]".format(data.itemId.min(), data.itemId.max()))

# DataLoader for training
sample_generator = SampleGenerator(ratings=data)
evaluate_data = sample_generator.evaluate_data
print("dataloader for training... done")

# Specify the exact model
print("start traing model")
config = gmf_config
engine = GMFEngine(config)
# config = mlp_config
# engine = MLPEngine(config)
# config = neumf_config
# engine = NeuMFEngine(config)
for epoch in range(config["num_epoch"]):
    print("Epoch {} starts !".format(epoch))
    print("-" * 80)
    train_loader = sample_generator.instance_a_train_loader(
        config["num_negative"], config["batch_size"]
    )
    engine.train_an_epoch(train_loader, epoch_id=epoch)
    hit_ratio, ndcg = engine.evaluate(evaluate_data, epoch_id=epoch)
    engine.save(config["alias"], epoch, hit_ratio, ndcg)
