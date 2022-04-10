import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from PIL import Image
import torch
import torchtuples as tt
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, transforms
from torch.optim import *
#import h5py
from pycox.datasets import metabric
from pycox.models import CoxPH
from pycox.evaluation import EvalSurv
from pycox.models import PCHazard
from pycox.models import LogisticHazard
from pycox.models import DeepHitSingle
from pycox.utils import kaplan_meier



def get_cox_model(pro_data_dir, cnn_model, cox_model_name, lr):

    """
    get cox model

    Args:
        proj_dir {path} -- project folder;
        cnn_model {model} -- cnn model;
        _cox_model {str} -- cox model name;
        lr {float} -- learning rate;
    
    Returns:
        cox model;

    """

    duration_index = np.load(os.path.join(pro_data_dir, 'duration_index.npy'))
    optimizer=torch.optim.Adam(cnn_model.parameters(), lr=lr)

    if cox_model_name == 'PCHazard':
        """
        The Piecewise Constant Hazard (PC-Hazard) model assumes that 
        the continuous-time hazard function is constant in predefined intervals. 
        It is similar to the Piecewise Exponential Models and PEANN, 
        but with a softplus activation instead of the exponential function.
        """
        cox_model = PCHazard(
            net=cnn_model,
            #optimizer=tt.optim.Adam(lr),
            optimizer=optimizer,
            duration_index=duration_index
            )
    elif cox_model_name == 'LogisticHazard':
        """
        The Logistic-Hazard method parametrize the discrete hazards and 
        optimize the survival likelihood. It is also called Partial Logistic 
        Regression and Nnet-survival.
        """
        cox_model = LogisticHazard(
            net=cnn_model,
            optimizer=optimizer,
            duration_index=duration_index
            )
    elif cox_model_name == 'DeepHitSingle':
        """
        DeepHit is a PMF method with a loss for improved ranking that can
        handle competing risks.
        """
        cox_model = DeepHitSingle(
            net=cnn_model, 
            optimizer=optimizer,
            alpha=0.2, 
            sigma=0.1, 
            duration_index=duration_index
            )
    elif cox_model_name == 'CoxPH':
        """
        CoxPH is a Cox proportional hazards model also referred to as DeepSurv.
        """
        cox_model = CoxPH(
            net=cnn_model,
            optimizer=optimizer
            )
    else:
        print('please select other cox models!')
    print('cox model:', cox_model_name)

    return cox_model
