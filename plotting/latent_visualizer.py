import seaborn as sns
import matplotlib.pyplot as plt
import glob
import os
import numpy as np
import matplotlib.gridspec as gridspec

from sklearn.manifold import TSNE
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
VIS_NUM = 200
G = 3
D = 3
ABN_IDX = 0


def load(path):
    ret = np.load(path, allow_pickle=True)
    ret = ret.tolist()
    return ret


def get_prob_dict(scores, labels):
    normal_hist = np.histogram(scores[labels==0], range=(np.min(scores), np.max(scores)), bins=200)
    abnormal_hist = np.histogram(scores[labels==1], range=(np.min(scores), np.max(scores)), bins=200)
    threshold = normal_hist[1]
    prob = abnormal_hist[0]/(normal_hist[0]+abnormal_hist[0])
    prob[np.isnan(prob)] = 1
    return prob, threshold[:-1]


def get_by_cls(d, cls):
    mean = d['mean']
    fake_latents = d['fake_latents']
    real_latents = d['real_latents']
    gt_labels = d['gt_labels']
    return mean[gt_labels==cls], fake_latents[gt_labels==cls], real_latents[gt_labels==cls]


def tsne(latents):
    tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)
    latents = tsne.fit_transform(latents)
    return latents


def compress(path):
    ret = load(path)
    latents = []
    mean_all_cls = []
    for i in range(10):
        mean, fake, real = get_by_cls(ret, i)
        fake = fake[:VIS_NUM]
        real = real[:VIS_NUM]
        mean_all_cls.append(mean[:VIS_NUM])

        print(fake.shape, real.shape)
        fake = fake.reshape(fake.shape[0], -1, fake.shape[-1])
        real = real.reshape(real.shape[0], -1, real.shape[-1])
        latent = np.concatenate([fake,real], axis=1)
        latents.append(latent.reshape(-1, latent.shape[-1]))
    latent_all_cls = np.vstack(latents)
    latent_all_cls = latent_all_cls.reshape(-1, 32)
    latent_all_cls = tsne(latent_all_cls)
    latent_all_cls = [latent_all_cls[i*VIS_NUM*(G+1)*D:i*VIS_NUM*(G+1)*D+VIS_NUM*(G+1)*D]
                      for i in range(10)]
    latent_all_cls = [latent.reshape(-1, (G+1)*D, 2) for latent in latent_all_cls]
    return latent_all_cls, mean_all_cls


def visualize(latent_all_cls, mean_all_cls):
    fig, axes = plt.subplots(nrows=5, ncols=6, figsize=(25,25))
    for j, ax in enumerate(axes.reshape(-1)):
        # for i, latent_one_cls in enumerate(latent_all_cls):
        idx_D = j%3
        latent_one_cls = latent_all_cls[j//3]
        mean_one_cls = np.mean(mean_all_cls[j//3], axis=1)[:, idx_D].copy()
        # mean_one_cls[mean_one_cls>0.25] = 1
        # mean_one_cls[mean_one_cls<=0.25] = 0

        fake, real = latent_one_cls[..., :D*G, :], latent_one_cls[..., D*G:, :]
        # x = np.where(mean_one_cls==1)
        ax.scatter(x=real[..., idx_D, 0], y=real[..., idx_D, 1], c= mean_one_cls, alpha=0.5, s=5)
        # ax.scatter(x=real[..., idx_D, 0][mean_one_cls==1], y=real[..., idx_D, 1][mean_one_cls==1],alpha=1, s=10)
        # ax.scatter(x=real[..., idx_D, 0][mean_one_cls==0], y=real[..., idx_D, 1][mean_one_cls==0], alpha=1, s=10)
        ax.set_xlim(-10,10)
        ax.set_ylim(-10,10)
        fig.add_subplot(ax)
    # plt.colorbar()

    plt.show()


if __name__ == '__main__':
    train_path = "../plane_as_abn_cls_all_info/mxn/train/mxn_airplane_3exp_6epoch_0abnidx_score_train.npy"
    test_path = "../plane_as_abn_cls_all_info/mxn/test/mxn_airplane_3exp_6epoch_0abnidx_score_train.npy"
    train_latent_all_cls, _ = compress(train_path)
    test_latent_all_cls, _ = compress(test_path)

    # visualize(latent_all_cls, mean_all_cls)
    pass

