import json
import os
import random
import shutil
import string
from pathlib import Path
from typing import List

import deepspeed.comm as dist
import pytest
import torch
import torch.distributed
from transformers import TrainingArguments

from oobleck.csrc.planning.pipeline_template import (
    LayerExecutionResult,
    LayerExecutionResults,
    PipelineTemplate,
    StageExecutionResult,
)
from oobleck.execution.dataloader import LoaderType, OobleckDataLoader
from oobleck.execution.dataset import OobleckDataset
from oobleck.execution.pipeline import OobleckPipeline
from oobleck.module.model import OobleckModel

TRAIN_BATCH_SIZE = 8
EVAL_BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEP = 2


@pytest.fixture(scope="session")
def wikitext_dataset():
    return OobleckDataset("gpt2", "wikitext", "wikitext-2-raw-v1")


@pytest.fixture(scope="session")
def imagenet_dataset():
    return OobleckDataset("microsoft/resnet-50", "Maysee/tiny-imagenet")


# OobleckDataset does not have any states and ok to use for the entire session.
@pytest.fixture(scope="session", params=["wikitext_dataset", "imagenet_dataset"])
def dataset(request: pytest.FixtureRequest):
    return request.getfixturevalue(request.param)


def gpt2_model(wikitext_dataset):
    # Refer to oobleck/examples/*.py for model arguments
    # gpt2-medium
    model_args = {
        "num_hidden_layers": 32,
        "n_positions": 1024,
        "n_embd": 1024,
        "n_head": 16,
    }
    return OobleckModel("gpt2", wikitext_dataset.sample, None, "test", model_args)


def resnet_model(imagenet_dataset):
    return OobleckModel(
        "microsoft/resnet-50", imagenet_dataset.sample, None, "test", None
    )


@pytest.fixture(
    scope="session",
    params=[
        (gpt2_model, "wikitext_dataset"),
        (resnet_model, "imagenet_dataset"),
    ],
    ids=["gpt2", "microsoft/resnet-50"],
)
def model(request: pytest.FixtureRequest):
    return request.param[0](request.getfixturevalue(request.param[1]))


@pytest.fixture(
    scope="function",
    params=[
        (gpt2_model, "wikitext_dataset"),
        (resnet_model, "imagenet_dataset"),
    ],
    ids=["gpt2", "microsoft/resnet-50"],
)
def model_function(no_distributed, request: pytest.FixtureRequest):
    return request.param[0](request.getfixturevalue(request.param[1]))


_model_datasets = {
    "gpt2": "wikitext_dataset",
    "microsoft/resnet-50": "imagenet_dataset",
}


@pytest.fixture(scope="session")
def dataloaders(model: OobleckModel, request: pytest.FixtureRequest):
    dataset = request.getfixturevalue(_model_datasets[model.model_name])

    training_args = TrainingArguments(
        output_dir="/tmp/test_output",
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=EVAL_BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEP,
    )

    training_dataloader = OobleckDataLoader(
        dataset,
        training_args,
        LoaderType.Training,
        # total number of microbatches.
        # Currently only have one process, so it should be the same as
        # gradient_accumulation_steps.
        training_args.gradient_accumulation_steps,
        0,
        0,
    )
    eval_dataloader = OobleckDataLoader(
        dataset,
        training_args,
        LoaderType.Evaluation,
        # total number of microbatches.
        # Currently only have one process, so it should be the same as
        # gradient_accumulation_steps.
        training_args.gradient_accumulation_steps,
        0,
        0,
    )
    return training_dataloader, eval_dataloader


@pytest.fixture(scope="session")
def model_dataloaders(model: OobleckModel, request: pytest.FixtureRequest):
    loaders = request.getfixturevalue("dataloaders")
    return model, loaders[0], loaders[1]


@pytest.fixture(scope="session")
def dummy_profile_results(model: OobleckModel):
    num_layers = len(model.model)
    layers = []
    allreduce_across_nodes = []
    allreduce_in_node = []
    for _ in range(num_layers):
        layers.append(
            {
                "forward": random.random(),
                "backward": random.random() * 3,
                "mem_required": [1024, 1024],
            }
        )

        # TODO: get argument to set number of nodes
        ar_across_nodes = {}
        for i in range(1, 33):
            ar_across_nodes[i] = random.random() * 4

        allreduce_across_nodes.append(ar_across_nodes)
        allreduce_in_node.append(
            {1: random.random(), 2: random.random(), 4: random.random()}
        )

    return layers, allreduce_across_nodes, allreduce_in_node


@pytest.fixture(scope="function")
def new_profile_directory(model):
    # This fixture is used to clean up the files created by profile.
    exist = True
    while exist:
        random_tag = "".join(random.choices(string.ascii_letters, k=8))
        path = Path(f"/tmp/oobleck/profiles/{model.model_name}-{random_tag}")
        exist = path.exists()
    yield random_tag
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture(scope="function")
def dummy_profile_result_files(
    model: OobleckModel, dummy_profile_results, new_profile_directory
):
    directory = Path(
        f"/tmp/oobleck/profiles/{model.model_name}-{new_profile_directory}"
    )
    directory.mkdir(parents=True, exist_ok=False)

    def _create_files(microbatch_size: int):
        filenames = [
            f"mb{microbatch_size}.json",
            "allreduce_across_nodes.json",
            "allreduce_in_node.json",
        ]
        for filename, result in zip(filenames, dummy_profile_results):
            with directory.joinpath(filename).open(mode="w") as f:
                json.dump(result, f)
                f.flush()

    yield _create_files


@pytest.fixture(scope="session")
def dummy_layer_execution_results(model: OobleckModel, dummy_profile_results):
    layers, allreduce_across_nodes, allreduce_in_node = dummy_profile_results

    results: List[LayerExecutionResult] = []
    for layer, execution, ar_in_node, ar_across_nodes in zip(
        model.model, layers, allreduce_in_node, allreduce_across_nodes
    ):
        results.append(
            LayerExecutionResult(
                layer.index,
                execution["forward"],
                execution["backward"],
                ar_in_node,
                ar_across_nodes,
                execution["mem_required"],
            )
        )
    return LayerExecutionResults(results)


@pytest.fixture(scope="function")
def no_distributed():
    original_env = dict(os.environ)
    os.environ.pop("MASTER_ADDR", None)
    os.environ.pop("MASTER_PORT", None)
    os.environ.pop("WORLD_SIZE", None)
    os.environ.pop("RANK", None)
    os.environ.pop("LOCAL_RANK", None)
    next(set_number_of_gpus(1))
    yield
    os.environ.clear()
    os.environ.update(original_env)

def set_number_of_gpus(num_gpus: int = 1):
    # Hack to make torch.cuda.device_count() return # GPUs specified in env
    func = torch.cuda.device_count
    torch.cuda.device_count = lambda: num_gpus
    os.environ["CUDA_VISIBLE_DEVICES"] = ",".join([str(i) for i in range(0, num_gpus)])
    yield
    torch.cuda.device_count = func
    os.environ.pop("CUDA_VISIBLE_DEVICES", None)


@pytest.fixture(scope="function")
def init_distributed():
    original_env = dict(os.environ)
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "0"
    os.environ["WORLD_SIZE"] = "1"
    os.environ["RANK"] = "0"
    os.environ["LOCAL_RANK"] = "0"

    set_number_of_gpus(1)

    def _distributed(init_required: bool):
        if init_required:
            if dist.is_initialized():
                return

            dist.init_distributed(dist_backend="nccl", dist_init_required=True, rank=0, world_size=1)
            assert dist.is_initialized()
        else:
            assert not dist.is_initialized()

    yield _distributed

    if dist.is_initialized():
        dist.destroy_process_group()
        dist.cdb = None
    assert not dist.is_initialized()
    
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="session")
def dummy_pipeline_template(dummy_layer_execution_results: LayerExecutionResults):
    def get_layer_split_indices(
        layers: List[LayerExecutionResult], num: int
    ) -> List[List[LayerExecutionResult]]:
        return [round(len(layers) * i / num) for i in range(1, num)]

    def _create_pipeline_template(num_gpus: int) -> PipelineTemplate:
        layers = dummy_layer_execution_results.get()
        layer_results = LayerExecutionResults(layers)
        indices = get_layer_split_indices(layers, num_gpus)
        stages = [
            StageExecutionResult(layer_results, indices, 1)
            for indices in zip([0] + indices, indices + [len(layers)])
        ]

        return PipelineTemplate(stages, 0.1, len(layers), num_gpus, 1)

    return _create_pipeline_template


@pytest.fixture(scope="function")
def dummy_pipeline(model_dataloaders, dummy_pipeline_template, init_distributed):
    def _create_pipelines(
        num_gpus_per_pipeline: int, ranks: List[int]
    ) -> List[OobleckPipeline]:
        assert len(ranks) % num_gpus_per_pipeline == 0, "Invalid number of ranks"
        assert len(ranks) <= torch.cuda.device_count(), "Too many ranks"

        model, train_dataloader, eval_dataloader = model_dataloaders
        init_distributed(True)
        training_args = TrainingArguments(
            output_dir="/tmp/test_output",
            per_device_train_batch_size=TRAIN_BATCH_SIZE,
            per_device_eval_batch_size=EVAL_BATCH_SIZE,
            gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEP,
        )

        pipeline_template = dummy_pipeline_template(num_gpus=num_gpus_per_pipeline)

        rank_groups = [
            ranks[i:num_gpus_per_pipeline]
            for i in range(0, len(ranks), num_gpus_per_pipeline)
        ]

        pipelines = [
            OobleckPipeline(
                pipeline_template=pipeline_template,
                model=model,
                dataloader=train_dataloader,
                step=0,
                ranks=rank_group,
                process_group=torch.distributed.new_group(ranks=rank_group),
                training_args=training_args,
            )
            for rank_group in rank_groups
        ]

        for pipeline in pipelines:
            assert all(
                all(p.is_cuda for p in layer.parameters())
                for layer in pipeline.model_layers
            )
            assert pipeline.is_first_stage() and pipeline.is_last_stage()

            num_pipe_buffers = pipeline.train_schedule.num_pipe_buffers()
            for buffer_name in ["inputs", "labels", "outputs"]:
                assert buffer_name in pipeline.pipe_buffers
                assert len(pipeline.pipe_buffers[buffer_name]) == num_pipe_buffers
                assert all(
                    buffer is None for buffer in pipeline.pipe_buffers[buffer_name]
                )

        return pipelines

    return _create_pipelines
