import os
import shutil

import numpy as np
import pandas as pd
import torch

from .common import fetch_pretrained_model, logger

from simpletransformers.classification import ClassificationModel as OriginalClassificationModel

manual_seed = 1234
train_args={
    "regression": True,
    "manual_seed": manual_seed,
    "silent": True,
}

def unzip_simple_transformer_model(model, model_folder, model_path):
    logger.info('Extracting file to folder')
    shutil.unpack_archive(model_path, model_folder)


class ClassificationModel(OriginalClassificationModel):
    def load_and_cache_examples(
        self, examples, evaluate=False, no_cache=False, multi_label=False, verbose=False, silent=False
    ):
        return super().load_and_cache_examples(examples, evaluate, no_cache, multi_label, verbose, silent)


class EmpathyClassifier():
    def __init__(self,
                 datapath,
                 use_cuda=torch.cuda.is_available(),
                 cuda_device=0,
                 batch_size=16):
        self.model_type = "empathy"
        train_args["eval_batch_size"] = batch_size

        model_path = os.path.join(datapath, "models/empathy/")
        model_file = os.path.join(datapath, "models/empathy.tar.gz")
        if not os.path.isdir(model_path):
            model = f'{self.model_type}_model'
            if not os.path.isfile(model_file):
                logger.info(f'Model {self.model_type} does not exist at {model_path}. Attempting to download it.')
                fetch_pretrained_model(model, model_file)
            unzip_simple_transformer_model(model, model_path, model_file)

        # Create a ClassificationModel
        self.model = ClassificationModel(
            'roberta',
            model_path,
            num_labels=1,
            use_cuda=use_cuda,
            cuda_device=cuda_device,
            args=train_args
        )

    def predict(self, text):
        if isinstance(text[0], str):
            text = [text]
        predictions, raw_outputs = self.model.predict(text)
        return raw_outputs
