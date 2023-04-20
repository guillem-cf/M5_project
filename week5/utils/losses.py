import torch.nn as nn
import torch.nn.functional as F


class ContrastiveLoss(nn.Module):
    """
    Contrastive loss
    Takes embeddings of two samples and a target label == 1 if samples are from the same class and label == 0 otherwise
    """

    def __init__(self, margin=1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin
        self.eps = 1e-9

    def forward(self, output1, output2, target, size_average=True):
        distances = (output2 - output1).pow(2).sum(1)  # squared distances
        losses = 0.5 * (target.float() * distances +
                        (1 + -1 * target).float() * F.relu(self.margin - (distances + self.eps).sqrt()).pow(2))
        return losses.mean() if size_average else losses.sum()


class TripletLoss(nn.Module):
    """
    Triplet loss
    Takes embeddings of an anchor sample, a positive sample and a negative sample
    """

    def __init__(self, margin):
        super(TripletLoss, self).__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative, step, size_average=True, wandb=None, epoch=0, batch_idx=0):
        distance_positive = (anchor - positive).pow(2).sum(1)  # .pow(.5) 
        distance_negative = (anchor - negative).pow(2).sum(1)  # .pow(.5)
            
        losses = F.relu(distance_positive - distance_negative + self.margin)
        
        if step == 0 and wandb is not None:
            distance_positive_print = distance_positive.mean()
            distance_negative_print = distance_negative.mean()
            print("distance_positive =", distance_positive_print)
            print("distance_negative =", distance_negative_print)
            wandb.log({'epoch': epoch, 'batch': batch_idx, 'positive_distance': distance_positive_print})
            wandb.log({'epoch': epoch, 'batch': batch_idx, 'negative_distance': distance_negative_print})
            
        return losses.mean() if size_average else losses.sum()
