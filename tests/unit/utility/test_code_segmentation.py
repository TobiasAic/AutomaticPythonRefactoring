import pytest

from utility.code_segmentation import CodeBlock, CodeSegmentation


def test_code_block_length():
    assert CodeBlock(0, 0).length() == 1
    assert CodeBlock(2, 5).length() == 4


def test_new_segmentation_has_one_block_spanning_all_lines():
    segmentation = CodeSegmentation(10)

    blocks = segmentation.get_blocks()

    assert blocks == [CodeBlock(0, 9)]


def test_first_and_next_and_prev_walk_the_blocks_in_order():
    segmentation = CodeSegmentation(10)
    segmentation.split_at(4)
    segmentation.split_at(7)

    first = segmentation.first()
    second = segmentation.next(first)
    third = segmentation.next(second)

    assert (first.start_line, first.end_line) == (0, 3)
    assert (second.start_line, second.end_line) == (4, 6)
    assert (third.start_line, third.end_line) == (7, 9)
    assert segmentation.next(third) is None
    assert segmentation.prev(first) is None
    assert segmentation.prev(second) is first
    assert segmentation.prev(third) is second


def test_split_at_rejects_out_of_bounds_lines():
    segmentation = CodeSegmentation(5)

    with pytest.raises(ValueError):
        segmentation.split_at(0)

    with pytest.raises(ValueError):
        segmentation.split_at(5)


def test_merge_with_next_recombines_blocks():
    segmentation = CodeSegmentation(10)
    segmentation.split_at(4)
    first = segmentation.first()

    merged = segmentation.merge_with_next(first)

    assert merged is first
    assert (merged.start_line, merged.end_line) == (0, 9)
    assert segmentation.get_blocks() == [CodeBlock(0, 9)]


def test_merge_with_next_raises_when_no_next_block():
    segmentation = CodeSegmentation(5)
    only_block = segmentation.first()

    with pytest.raises(ValueError):
        segmentation.merge_with_next(only_block)


def test_split_at_same_line_twice_is_idempotent():
    segmentation = CodeSegmentation(10)
    segmentation.split_at(4)
    segmentation.split_at(4)

    assert segmentation.get_blocks() == [CodeBlock(0, 3), CodeBlock(4, 9)]
