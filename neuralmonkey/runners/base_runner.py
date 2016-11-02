from typing import Any, Tuple, List, NamedTuple
import tensorflow as tf

from neuralmonkey.tf_manager import RunResult

# tests: pylint, mypy

# pylint: disable=invalid-name
ExecutionResult = NamedTuple('ExecutionResult',
                             [('outputs', List[Any]),
                              ('losses', List[float]),
                              ('scalar_summaries', tf.Summary),
                              ('histogram_summaries', tf.Summary),
                              ('image_summaries', tf.Summary)])


class Executable(object):

    def next_to_execute(self) -> Tuple[List[Any], List[tf.Tensor]]:
        raise NotImplementedError()

    def collect_results(self, results: List[List[RunResult]]) -> None:
        raise NotImplementedError()


def collect_encoders(coder):
    """Collect recusively all encoders and decoders."""
    if coder.hasattr('encoders'):
        return set([coder]) | set.union(collect_encoders(enc)
                                        for enc in coder.encoders)
    else:
        return set([coder])

class BaseRunner(object):

    def __init__(self, output_series: str, decoder) -> None:
        self.output_series = output_series
        self.decoder = decoder
        self.all_coders = collect_encoders(decoder)
        self.loss_names = []  # type: List[str]

    def get_executable(self, train=False) -> Executable:
        raise NotImplementedError()

    def collect_finished(self, execution_results: List[ExecutionResult]) -> ExecutionResult:
        outputs = []  # type: List[Any]
        losses_sum = [0. for _ in self.loss_names]
        for result in execution_results:
            outputs.extend(result.outputs)
            for i, loss in enumerate(result.losses):
                losses_sum[i] += loss
            # TODO aggregate TensorBoard summaries
        losses = [l / len(outputs) for l in losses_sum]
        return ExecutionResult(outputs, losses,
                               execution_results[0].plot_summaries,
                               execution_results[0].histogram_summaries,
                               execution_results[0].image_summaries)
