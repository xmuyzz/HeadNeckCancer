import os
import pandas as pd
import numpy as np
import torch
import random
from data_loader_transform import data_loader_transform
from train import train
from test import test
from get_cnn_model import get_cnn_model
from get_cox_model import get_cox_model
from opts import parse_opts
from get_data.data_loader2 import data_loader2


if __name__ == '__main__':

    opt = parse_opts()
    random.seed(opt.manual_seed)
    np.random.seed(opt.manual_seed)
    torch.manual_seed(opt.manual_seed)

    if opt.proj_dir is not None:
        opt.output_dir = os.path.join(opt.proj_dir, opt.output)
        opt.pro_data_dir = os.path.join(opt.proj_dir, opt.pro_data)
        opt.log_dir = os.path.join(opt.proj_dir, opt.log)
        opt.model_dir = os.path.join(opt.proj_dir, opt.model)
        if not os.path.exists(opt.output_dir):
            os.makedirs(opt.output_dir)
        if not os.path.exists(opt.pro_data_dir):
            os.makefirs(opt.pro_data_dir)
        if not os.path.exists(opt.log_dir):
            os.makedirs(opt.log_dir)
        if not os.path.exists(opt.model_dir):
            os.makedirs(opt.model_dir)

    if opt.augmentation:
        dl_train, dl_tune, dl_val, dl_test, dl_tune_cb, df_tune = data_loader_transform(
            pro_data_dir=opt.pro_data_dir, 
            batch_size=opt.batch_size, 
            _cox_model=opt.cox_model_name, 
            num_durations=opt.num_durations,
            _outcome_model=opt._outcome_model,
            tumor_type=opt.tumor_type,
            input_data_type=opt.input_data_type,
            i_kfold=opt.i_kfold)
    else:
        dl_train, dl_tune, dl_val = data_loader2(
            pro_data_dir=opt.pro_data_dir,
            batch_size=opt.batch_size,
            _cox_model=opt.cox_model_name,
            num_durations=opt.num_durations)
   
    if opt.train:
        """
        CNN Models
        Implemented:
            MobileNetV2, MobileNet, ResNet, ResNetV2, WideResNet, 
            ShuffleNet, ShuffleNetV2, DenseNet
        Not working:
            SqueezeNet, ResNeXt, ResNeXtV2, C3D,  

        """

        cnns = ['PreActResNet']
        model_depth = 50
        for cnn_name in cnns:   
            if cnn_name in ['resnet', 'ResNetV2', 'PreActResNet']:
                assert model_depth in [10, 18, 34, 50, 152, 200]
            elif cnn_name in ['ResNeXt', 'ResNeXtV2', 'WideResNet']:
                assert model_depth in [50, 101, 152, 200]
            elif cnn_name in ['DenseNet']:
                assert model_depth in [121, 169, 201]
            else:
                model_depth = None
            cnn_model = get_cnn_model(
                cnn_name=cnn_name,
                model_depth=model_depth,
                n_classes=opt.num_durations, 
                in_channels=opt.in_channels)
            cox_model = get_cox_model(
                pro_data_dir=opt.pro_data_dir,
                cnn_model=cnn_model,
                cox_model_name=opt.cox_model_name,
                lr=opt.lr)
            for epoch in [50]:
                for lr in [0.001]:
                    train(
                        output_dir=opt.output_dir,
                        pro_data_dir=opt.pro_data_dir,
                        log_dir=opt.log_dir,
                        model_dir=opt.model_dir,
                        cnn_model=cnn_model,
                        model_depth=model_depth,
                        cox_model=cox_model,
                        epochs=epoch,
                        dl_train=dl_train,
                        dl_tune=dl_tune,
                        dl_val=dl_val,
                        dl_tune_cb=dl_tune_cb,
                        df_tune=df_tune,
                        cnn_name=opt.cnn_name,
                        lr=lr)
    if opt.test:
        test(
            pro_data_dir=opt.pro_data_dir, 
            output_dir=opt.output_dir, 
            cox_model=cox_model, 
            load_model=opt.load_model, 
            dl_val=dl_val, 
            score_type=opt.score_type,
            cnn_name=opt.cnn_name, 
            epochs=opt.epoch,  
            lr=opt.lr)
