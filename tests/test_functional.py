from __future__ import absolute_import

import cv2
import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal_nulp

import albumentations as A
import albumentations.augmentations.functional as F
import albumentations.augmentations.geometric.functional as FGeometric
from albumentations.augmentations.utils import (
    get_opencv_dtype_from_numpy,
    is_multispectral_image,
)
from albumentations.core.bbox_utils import filter_bboxes
from albumentations.core.transforms_interface import BBoxesInternalType
from tests.utils import convert_2d_to_target_format


@pytest.mark.parametrize("target", ["image", "mask"])
def test_vflip(target):
    img = np.array([[1, 1, 1], [0, 1, 1], [0, 0, 1]], dtype=np.uint8)
    expected = np.array([[0, 0, 1], [0, 1, 1], [1, 1, 1]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    flipped_img = FGeometric.vflip(img)
    assert np.array_equal(flipped_img, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_vflip_float(target):
    img = np.array([[0.4, 0.4, 0.4], [0.0, 0.4, 0.4], [0.0, 0.0, 0.4]], dtype=np.float32)
    expected = np.array([[0.0, 0.0, 0.4], [0.0, 0.4, 0.4], [0.4, 0.4, 0.4]], dtype=np.float32)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    flipped_img = FGeometric.vflip(img)
    assert_array_almost_equal_nulp(flipped_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_hflip(target):
    img = np.array([[1, 1, 1], [0, 1, 1], [0, 0, 1]], dtype=np.uint8)
    expected = np.array([[1, 1, 1], [1, 1, 0], [1, 0, 0]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    flipped_img = FGeometric.hflip(img)
    assert np.array_equal(flipped_img, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_hflip_float(target):
    img = np.array([[0.4, 0.4, 0.4], [0.0, 0.4, 0.4], [0.0, 0.0, 0.4]], dtype=np.float32)
    expected = np.array([[0.4, 0.4, 0.4], [0.4, 0.4, 0.0], [0.4, 0.0, 0.0]], dtype=np.float32)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    flipped_img = FGeometric.hflip(img)
    assert_array_almost_equal_nulp(flipped_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
@pytest.mark.parametrize(
    ["code", "func"],
    [[0, FGeometric.vflip], [1, FGeometric.hflip], [-1, lambda img: FGeometric.vflip(FGeometric.hflip(img))]],
)
def test_random_flip(code, func, target):
    img = np.array([[1, 1, 1], [0, 1, 1], [0, 0, 1]], dtype=np.uint8)
    img = convert_2d_to_target_format([img], target=target)
    assert np.array_equal(FGeometric.random_flip(img, code), func(img))


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
@pytest.mark.parametrize(
    ["code", "func"],
    [[0, FGeometric.vflip], [1, FGeometric.hflip], [-1, lambda img: FGeometric.vflip(FGeometric.hflip(img))]],
)
def test_random_flip_float(code, func, target):
    img = np.array([[0.4, 0.4, 0.4], [0.0, 0.4, 0.4], [0.0, 0.0, 0.4]], dtype=np.float32)
    img = convert_2d_to_target_format([img], target=target)
    assert_array_almost_equal_nulp(FGeometric.random_flip(img, code), func(img))


@pytest.mark.parametrize(["input_shape", "expected_shape"], [[(128, 64), (64, 128)], [(128, 64, 3), (64, 128, 3)]])
def test_transpose(input_shape, expected_shape):
    img = np.random.randint(low=0, high=256, size=input_shape, dtype=np.uint8)
    transposed = FGeometric.transpose(img)
    assert transposed.shape == expected_shape


@pytest.mark.parametrize(["input_shape", "expected_shape"], [[(128, 64), (64, 128)], [(128, 64, 3), (64, 128, 3)]])
def test_transpose_float(input_shape, expected_shape):
    img = np.random.uniform(low=0.0, high=1.0, size=input_shape).astype("float32")
    transposed = FGeometric.transpose(img)
    assert transposed.shape == expected_shape


@pytest.mark.parametrize("target", ["image", "mask"])
def test_rot90(target):
    img = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1]], dtype=np.uint8)
    expected = np.array([[1, 1, 1], [0, 0, 0], [0, 0, 0]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    rotated = FGeometric.rot90(img, factor=1)
    assert np.array_equal(rotated, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_rot90_float(target):
    img = np.array([[0.0, 0.0, 0.4], [0.0, 0.0, 0.4], [0.0, 0.0, 0.4]], dtype=np.float32)
    expected = np.array([[0.4, 0.4, 0.4], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], dtype=np.float32)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    rotated = FGeometric.rot90(img, factor=1)
    assert_array_almost_equal_nulp(rotated, expected)


def test_normalize():
    img = np.ones((100, 100, 3), dtype=np.uint8) * 127
    normalized = F.normalize(img, mean=50, std=3)
    expected = (np.ones((100, 100, 3), dtype=np.float32) * 127 / 255 - 50) / 3
    assert_array_almost_equal_nulp(normalized, expected)


def test_normalize_float():
    img = np.ones((100, 100, 3), dtype=np.float32) * 0.4
    normalized = F.normalize(img, mean=50, std=3, max_pixel_value=1.0)
    expected = (np.ones((100, 100, 3), dtype=np.float32) * 0.4 - 50) / 3
    assert_array_almost_equal_nulp(normalized, expected)


def test_compare_rotate_and_shift_scale_rotate(image):
    rotated_img_1 = FGeometric.rotate(image, angle=60)
    rotated_img_2 = FGeometric.shift_scale_rotate(image, angle=60, scale=1, dx=0, dy=0)
    assert np.array_equal(rotated_img_1, rotated_img_2)


def test_compare_rotate_float_and_shift_scale_rotate_float(float_image):
    rotated_img_1 = FGeometric.rotate(float_image, angle=60)
    rotated_img_2 = FGeometric.shift_scale_rotate(float_image, angle=60, scale=1, dx=0, dy=0)
    assert np.array_equal(rotated_img_1, rotated_img_2)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_center_crop(target):
    img = np.array([[1, 1, 1, 1], [0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1]], dtype=np.uint8)
    expected = np.array([[1, 1], [0, 1]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    cropped_img = A.center_crop(img, 2, 2)
    assert np.array_equal(cropped_img, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_center_crop_float(target):
    img = np.array(
        [[0.4, 0.4, 0.4, 0.4], [0.0, 0.4, 0.4, 0.4], [0.0, 0.0, 0.4, 0.4], [0.0, 0.0, 0.0, 0.4]], dtype=np.float32
    )
    expected = np.array([[0.4, 0.4], [0.0, 0.4]], dtype=np.float32)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    cropped_img = A.center_crop(img, 2, 2)
    assert_array_almost_equal_nulp(cropped_img, expected)


def test_center_crop_with_incorrectly_large_crop_size():
    img = np.ones((4, 4), dtype=np.uint8)
    with pytest.raises(ValueError) as exc_info:
        A.center_crop(img, 8, 8)
    assert str(exc_info.value) == "Requested crop size (8, 8) is larger than the image size (4, 4)"


@pytest.mark.parametrize("target", ["image", "mask"])
def test_random_crop(target):
    img = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], dtype=np.uint8)
    expected = np.array([[5, 6], [9, 10]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    cropped_img = A.random_crop(img, crop_height=2, crop_width=2, h_start=0.5, w_start=0)
    assert np.array_equal(cropped_img, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_random_crop_float(target):
    img = np.array(
        [[0.01, 0.02, 0.03, 0.04], [0.05, 0.06, 0.07, 0.08], [0.09, 0.10, 0.11, 0.12], [0.13, 0.14, 0.15, 0.16]],
        dtype=np.float32,
    )
    expected = np.array([[0.05, 0.06], [0.09, 0.10]], dtype=np.float32)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    cropped_img = A.random_crop(img, crop_height=2, crop_width=2, h_start=0.5, w_start=0)
    assert_array_almost_equal_nulp(cropped_img, expected)


def test_random_crop_with_incorrectly_large_crop_size():
    img = np.ones((4, 4), dtype=np.uint8)
    with pytest.raises(ValueError) as exc_info:
        A.random_crop(img, crop_height=8, crop_width=8, h_start=0, w_start=0)
    assert str(exc_info.value) == "Requested crop size (8, 8) is larger than the image size (4, 4)"


def test_random_crop_extrema():
    img = np.indices((4, 4), dtype=np.uint8).transpose([1, 2, 0])
    expected1 = np.indices((2, 2), dtype=np.uint8).transpose([1, 2, 0])
    expected2 = expected1 + 2
    cropped_img1 = A.random_crop(img, crop_height=2, crop_width=2, h_start=0.0, w_start=0.0)
    cropped_img2 = A.random_crop(img, crop_height=2, crop_width=2, h_start=0.9999, w_start=0.9999)
    assert np.array_equal(cropped_img1, expected1)
    assert np.array_equal(cropped_img2, expected2)


def test_clip():
    img = np.array([[-300, 0], [100, 400]], dtype=np.float32)
    expected = np.array([[0, 0], [100, 255]], dtype=np.float32)
    clipped = F.clip(img, dtype=np.uint8, maxval=255)
    assert np.array_equal(clipped, expected)


def test_clip_float():
    img = np.array([[-0.02, 0], [0.5, 2.2]], dtype=np.float32)
    expected = np.array([[0, 0], [0.5, 1.0]], dtype=np.float32)
    clipped = F.clip(img, dtype=np.float32, maxval=1.0)
    assert_array_almost_equal_nulp(clipped, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_pad(target):
    img = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    expected = np.array([[4, 3, 4, 3], [2, 1, 2, 1], [4, 3, 4, 3], [2, 1, 2, 1]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    padded = FGeometric.pad(img, min_height=4, min_width=4)
    assert np.array_equal(padded, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_pad_float(target):
    img = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    expected = np.array(
        [[0.4, 0.3, 0.4, 0.3], [0.2, 0.1, 0.2, 0.1], [0.4, 0.3, 0.4, 0.3], [0.2, 0.1, 0.2, 0.1]], dtype=np.float32
    )
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    padded_img = FGeometric.pad(img, min_height=4, min_width=4)
    assert_array_almost_equal_nulp(padded_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_rotate_from_shift_scale_rotate(target):
    img = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], dtype=np.uint8)
    expected = np.array([[4, 8, 12, 16], [3, 7, 11, 15], [2, 6, 10, 14], [1, 5, 9, 13]], dtype=np.uint8)

    img, expected = convert_2d_to_target_format([img, expected], target=target)
    rotated_img = FGeometric.shift_scale_rotate(
        img, angle=90, scale=1, dx=0, dy=0, interpolation=cv2.INTER_NEAREST, border_mode=cv2.BORDER_CONSTANT
    )
    assert np.array_equal(rotated_img, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_rotate_float_from_shift_scale_rotate(target):
    img = np.array(
        [[0.01, 0.02, 0.03, 0.04], [0.05, 0.06, 0.07, 0.08], [0.09, 0.10, 0.11, 0.12], [0.13, 0.14, 0.15, 0.16]],
        dtype=np.float32,
    )
    expected = np.array(
        [[0.04, 0.08, 0.12, 0.16], [0.03, 0.07, 0.11, 0.15], [0.02, 0.06, 0.10, 0.14], [0.01, 0.05, 0.09, 0.13]],
        dtype=np.float32,
    )
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    rotated_img = FGeometric.shift_scale_rotate(
        img, angle=90, scale=1, dx=0, dy=0, interpolation=cv2.INTER_NEAREST, border_mode=cv2.BORDER_CONSTANT
    )
    assert_array_almost_equal_nulp(rotated_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_scale_from_shift_scale_rotate(target):
    img = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], dtype=np.uint8)
    expected = np.array([[6, 6, 7, 7], [6, 6, 7, 7], [10, 10, 11, 11], [10, 10, 11, 11]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    scaled_img = FGeometric.shift_scale_rotate(
        img, angle=0, scale=2, dx=0, dy=0, interpolation=cv2.INTER_NEAREST, border_mode=cv2.BORDER_CONSTANT
    )
    assert np.array_equal(scaled_img, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_scale_float_from_shift_scale_rotate(target):
    img = np.array(
        [[0.01, 0.02, 0.03, 0.04], [0.05, 0.06, 0.07, 0.08], [0.09, 0.10, 0.11, 0.12], [0.13, 0.14, 0.15, 0.16]],
        dtype=np.float32,
    )
    expected = np.array(
        [[0.06, 0.06, 0.07, 0.07], [0.06, 0.06, 0.07, 0.07], [0.10, 0.10, 0.11, 0.11], [0.10, 0.10, 0.11, 0.11]],
        dtype=np.float32,
    )
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    scaled_img = FGeometric.shift_scale_rotate(
        img, angle=0, scale=2, dx=0, dy=0, interpolation=cv2.INTER_NEAREST, border_mode=cv2.BORDER_CONSTANT
    )
    assert_array_almost_equal_nulp(scaled_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_shift_x_from_shift_scale_rotate(target):
    img = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], dtype=np.uint8)
    expected = np.array([[0, 0, 1, 2], [0, 0, 5, 6], [0, 0, 9, 10], [0, 0, 13, 14]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    shifted_along_x_img = FGeometric.shift_scale_rotate(
        img, angle=0, scale=1, dx=0.5, dy=0, interpolation=cv2.INTER_NEAREST, border_mode=cv2.BORDER_CONSTANT
    )
    assert np.array_equal(shifted_along_x_img, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_shift_x_float_from_shift_scale_rotate(target):
    img = np.array(
        [[0.01, 0.02, 0.03, 0.04], [0.05, 0.06, 0.07, 0.08], [0.09, 0.10, 0.11, 0.12], [0.13, 0.14, 0.15, 0.16]],
        dtype=np.float32,
    )
    expected = np.array(
        [[0.00, 0.00, 0.01, 0.02], [0.00, 0.00, 0.05, 0.06], [0.00, 0.00, 0.09, 0.10], [0.00, 0.00, 0.13, 0.14]],
        dtype=np.float32,
    )
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    shifted_along_x_img = FGeometric.shift_scale_rotate(
        img, angle=0, scale=1, dx=0.5, dy=0, interpolation=cv2.INTER_NEAREST, border_mode=cv2.BORDER_CONSTANT
    )
    assert_array_almost_equal_nulp(shifted_along_x_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_shift_y_from_shift_scale_rotate(target):
    img = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]], dtype=np.uint8)
    expected = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [1, 2, 3, 4], [5, 6, 7, 8]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    shifted_along_y_img = FGeometric.shift_scale_rotate(
        img, angle=0, scale=1, dx=0, dy=0.5, interpolation=cv2.INTER_NEAREST, border_mode=cv2.BORDER_CONSTANT
    )
    assert np.array_equal(shifted_along_y_img, expected)


@pytest.mark.parametrize("target", ["image", "image_4_channels"])
def test_shift_y_float_from_shift_scale_rotate(target):
    img = np.array(
        [[0.01, 0.02, 0.03, 0.04], [0.05, 0.06, 0.07, 0.08], [0.09, 0.10, 0.11, 0.12], [0.13, 0.14, 0.15, 0.16]],
        dtype=np.float32,
    )
    expected = np.array(
        [[0.00, 0.00, 0.00, 0.00], [0.00, 0.00, 0.00, 0.00], [0.01, 0.02, 0.03, 0.04], [0.05, 0.06, 0.07, 0.08]],
        dtype=np.float32,
    )
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    shifted_along_y_img = FGeometric.shift_scale_rotate(
        img, angle=0, scale=1, dx=0, dy=0.5, interpolation=cv2.INTER_NEAREST, border_mode=cv2.BORDER_CONSTANT
    )
    assert_array_almost_equal_nulp(shifted_along_y_img, expected)


@pytest.mark.parametrize(
    ["shift_params", "expected"], [[(-10, 0, 10), (117, 127, 137)], [(-200, 0, 200), (0, 127, 255)]]
)
def test_shift_rgb(shift_params, expected):
    img = np.ones((100, 100, 3), dtype=np.uint8) * 127
    r_shift, g_shift, b_shift = shift_params
    img = F.shift_rgb(img, r_shift=r_shift, g_shift=g_shift, b_shift=b_shift)
    expected_r, expected_g, expected_b = expected
    assert img.dtype == np.dtype("uint8")
    assert (img[:, :, 0] == expected_r).all()
    assert (img[:, :, 1] == expected_g).all()
    assert (img[:, :, 2] == expected_b).all()


@pytest.mark.parametrize(
    ["shift_params", "expected"], [[(-0.1, 0, 0.1), (0.3, 0.4, 0.5)], [(-0.6, 0, 0.6), (0, 0.4, 1.0)]]
)
def test_shift_rgb_float(shift_params, expected):
    img = np.ones((100, 100, 3), dtype=np.float32) * 0.4
    r_shift, g_shift, b_shift = shift_params
    img = F.shift_rgb(img, r_shift=r_shift, g_shift=g_shift, b_shift=b_shift)
    expected_r, expected_g, expected_b = [
        np.ones((100, 100), dtype=np.float32) * channel_value for channel_value in expected
    ]
    assert img.dtype == np.dtype("float32")
    assert_array_almost_equal_nulp(img[:, :, 0], expected_r)
    assert_array_almost_equal_nulp(img[:, :, 1], expected_g)
    assert_array_almost_equal_nulp(img[:, :, 2], expected_b)


@pytest.mark.parametrize(["alpha", "expected"], [(1.5, 190), (3, 255)])
def test_random_contrast(alpha, expected):
    img = np.ones((100, 100, 3), dtype=np.uint8) * 127
    img = F.brightness_contrast_adjust(img, alpha=alpha)
    assert img.dtype == np.dtype("uint8")
    assert (img == expected).all()


@pytest.mark.parametrize(["alpha", "expected"], [(1.5, 0.6), (3, 1.0)])
def test_random_contrast_float(alpha, expected):
    img = np.ones((100, 100, 3), dtype=np.float32) * 0.4
    expected = np.ones((100, 100, 3), dtype=np.float32) * expected
    img = F.brightness_contrast_adjust(img, alpha=alpha)
    assert img.dtype == np.dtype("float32")
    assert_array_almost_equal_nulp(img, expected)


@pytest.mark.parametrize(["beta", "expected"], [(-0.5, 50), (0.25, 125)])
def test_random_brightness(beta, expected):
    img = np.ones((100, 100, 3), dtype=np.uint8) * 100
    img = F.brightness_contrast_adjust(img, beta=beta)
    assert img.dtype == np.dtype("uint8")
    assert (img == expected).all()


@pytest.mark.parametrize(["beta", "expected"], [(0.2, 0.48), (-0.1, 0.36)])
def test_random_brightness_float(beta, expected):
    img = np.ones((100, 100, 3), dtype=np.float32) * 0.4
    expected = np.ones_like(img) * expected
    img = F.brightness_contrast_adjust(img, beta=beta)
    assert img.dtype == np.dtype("float32")
    assert_array_almost_equal_nulp(img, expected)


@pytest.mark.parametrize(["gamma", "expected"], [(1, 1), (0.8, 3)])
def test_gamma_transform(gamma, expected):
    img = np.ones((100, 100, 3), dtype=np.uint8)
    img = F.gamma_transform(img, gamma=gamma)
    assert img.dtype == np.dtype("uint8")
    assert (img == expected).all()


@pytest.mark.parametrize(["gamma", "expected"], [(1, 0.4), (10, 0.00010486)])
def test_gamma_transform_float(gamma, expected):
    img = np.ones((100, 100, 3), dtype=np.float32) * 0.4
    expected = np.ones((100, 100, 3), dtype=np.float32) * expected
    img = F.gamma_transform(img, gamma=gamma)
    assert img.dtype == np.dtype("float32")
    assert np.allclose(img, expected)


def test_gamma_float_equal_uint8():
    img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    img_f = img.astype(np.float32) / 255.0
    gamma = 0.5

    img = F.gamma_transform(img, gamma)
    img_f = F.gamma_transform(img_f, gamma)

    img = img.astype(np.float32)
    img_f *= 255.0

    assert (np.abs(img - img_f) <= 1).all()


@pytest.mark.parametrize(["dtype", "divider"], [(np.uint8, 255), (np.uint16, 65535), (np.uint32, 4294967295)])
def test_to_float_without_max_value_specified(dtype, divider):
    img = np.ones((100, 100, 3), dtype=dtype)
    expected = img.astype("float32") / divider
    assert_array_almost_equal_nulp(F.to_float(img), expected)


@pytest.mark.parametrize("max_value", [255.0, 65535.0, 4294967295.0])
def test_to_float_with_max_value_specified(max_value):
    img = np.ones((100, 100, 3), dtype=np.uint16)
    expected = img.astype("float32") / max_value
    assert_array_almost_equal_nulp(F.to_float(img, max_value=max_value), expected)


def test_to_float_unknown_dtype():
    img = np.ones((100, 100, 3), dtype=np.int16)
    with pytest.raises(RuntimeError) as exc_info:
        F.to_float(img)
    assert str(exc_info.value) == (
        "Can't infer the maximum value for dtype int16. You need to specify the maximum value manually by passing "
        "the max_value argument"
    )


@pytest.mark.parametrize("max_value", [255.0, 65535.0, 4294967295.0])
def test_to_float_unknown_dtype_with_max_value(max_value):
    img = np.ones((100, 100, 3), dtype=np.int16)
    expected = img.astype("float32") / max_value
    assert_array_almost_equal_nulp(F.to_float(img, max_value=max_value), expected)


@pytest.mark.parametrize(["dtype", "multiplier"], [(np.uint8, 255), (np.uint16, 65535), (np.uint32, 4294967295)])
def test_from_float_without_max_value_specified(dtype, multiplier):
    img = np.ones((100, 100, 3), dtype=np.float32)
    expected = (img * multiplier).astype(dtype)
    assert_array_almost_equal_nulp(F.from_float(img, np.dtype(dtype)), expected)


@pytest.mark.parametrize("max_value", [255.0, 65535.0, 4294967295.0])
def test_from_float_with_max_value_specified(max_value):
    img = np.ones((100, 100, 3), dtype=np.float32)
    expected = (img * max_value).astype(np.uint32)
    assert_array_almost_equal_nulp(F.from_float(img, dtype=np.uint32, max_value=max_value), expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_scale(target):
    img = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]], dtype=np.uint8)
    expected = np.array(
        [
            [1, 1, 2, 2, 3, 3],
            [2, 2, 2, 3, 3, 4],
            [3, 3, 4, 4, 5, 5],
            [5, 5, 5, 6, 6, 7],
            [6, 6, 7, 7, 8, 8],
            [8, 8, 8, 9, 9, 10],
            [9, 9, 10, 10, 11, 11],
            [10, 10, 11, 11, 12, 12],
        ],
        dtype=np.uint8,
    )

    img, expected = convert_2d_to_target_format([img, expected], target=target)
    scaled = FGeometric.scale(img, scale=2, interpolation=cv2.INTER_LINEAR)
    assert np.array_equal(scaled, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_longest_max_size(target):
    img = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]], dtype=np.uint8)
    expected = np.array([[2, 3], [6, 7], [10, 11]], dtype=np.uint8)

    img, expected = convert_2d_to_target_format([img, expected], target=target)
    scaled = FGeometric.longest_max_size(img, max_size=3, interpolation=cv2.INTER_LINEAR)
    assert np.array_equal(scaled, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_smallest_max_size(target):
    img = np.array(
        [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12], [12, 13, 14, 15, 16, 17], [18, 19, 20, 21, 22, 23]], dtype=np.uint8
    )
    expected = np.array([[2, 4, 5, 7], [10, 11, 13, 14], [17, 19, 20, 22]], dtype=np.uint8)

    img, expected = convert_2d_to_target_format([img, expected], target=target)
    scaled = FGeometric.smallest_max_size(img, max_size=3, interpolation=cv2.INTER_LINEAR)
    assert np.array_equal(scaled, expected)


def test_from_float_unknown_dtype():
    img = np.ones((100, 100, 3), dtype=np.float32)
    with pytest.raises(RuntimeError) as exc_info:
        F.from_float(img, np.dtype(np.int16))
    assert str(exc_info.value) == (
        "Can't infer the maximum value for dtype int16. You need to specify the maximum value manually by passing "
        "the max_value argument"
    )


@pytest.mark.parametrize("target", ["image", "mask"])
def test_resize_default_interpolation(target):
    img = np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]], dtype=np.uint8)
    expected = np.array([[2, 2], [4, 4]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    resized_img = FGeometric.resize(img, 2, 2)
    height, width = resized_img.shape[:2]
    assert height == 2
    assert width == 2
    assert np.array_equal(resized_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_resize_nearest_interpolation(target):
    img = np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]], dtype=np.uint8)
    expected = np.array([[1, 1], [3, 3]], dtype=np.uint8)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    resized_img = FGeometric.resize(img, 2, 2, interpolation=cv2.INTER_NEAREST)
    height, width = resized_img.shape[:2]
    assert height == 2
    assert width == 2
    assert np.array_equal(resized_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_resize_different_height_and_width(target):
    img = np.ones((100, 100), dtype=np.uint8)
    img = convert_2d_to_target_format([img], target=target)
    resized_img = FGeometric.resize(img, height=20, width=30)
    height, width = resized_img.shape[:2]
    assert height == 20
    assert width == 30
    if target == "image":
        num_channels = resized_img.shape[2]
        assert num_channels == 3


@pytest.mark.parametrize("target", ["image", "mask"])
def test_resize_default_interpolation_float(target):
    img = np.array(
        [[0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2], [0.3, 0.3, 0.3, 0.3], [0.4, 0.4, 0.4, 0.4]], dtype=np.float32
    )
    expected = np.array([[0.15, 0.15], [0.35, 0.35]], dtype=np.float32)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    resized_img = FGeometric.resize(img, 2, 2)
    height, width = resized_img.shape[:2]
    assert height == 2
    assert width == 2
    assert_array_almost_equal_nulp(resized_img, expected)


@pytest.mark.parametrize("target", ["image", "mask"])
def test_resize_nearest_interpolation_float(target):
    img = np.array(
        [[0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2], [0.3, 0.3, 0.3, 0.3], [0.4, 0.4, 0.4, 0.4]], dtype=np.float32
    )
    expected = np.array([[0.1, 0.1], [0.3, 0.3]], dtype=np.float32)
    img, expected = convert_2d_to_target_format([img, expected], target=target)
    resized_img = FGeometric.resize(img, 2, 2, interpolation=cv2.INTER_NEAREST)
    height, width = resized_img.shape[:2]
    assert height == 2
    assert width == 2
    assert np.array_equal(resized_img, expected)


@pytest.mark.parametrize(
    "bboxes, target",
    [
        (np.array([(0.1, 0.2, 0.6, 0.5)]), np.array([(0.1, 0.5, 0.6, 0.8)])),
    ],
)
def test_bboxes_vflip(bboxes, target):
    bboxes = BBoxesInternalType(array=bboxes)
    assert np.array_equal(FGeometric.bboxes_vflip(bboxes).array, target)


@pytest.mark.parametrize(
    "bboxes, target",
    [
        (np.array([(0.1, 0.2, 0.6, 0.5)]), np.array([(0.4, 0.2, 0.9, 0.5)])),
    ],
)
def test_bboxes_hflip(bboxes, target):
    bboxes = BBoxesInternalType(array=bboxes)
    assert np.array_equal(FGeometric.bboxes_hflip(bboxes).array, target)


@pytest.mark.parametrize(
    "axis, func, bboxes",
    [
        (0, FGeometric.bboxes_vflip, np.array([[0.1, 0.2, 0.6, 0.5]])),
        (1, FGeometric.bboxes_hflip, np.array([[0.1, 0.2, 0.6, 0.5]])),
        (-1, lambda bboxes: FGeometric.bboxes_vflip(FGeometric.bboxes_hflip(bboxes)), np.array([[0.1, 0.2, 0.6, 0.5]])),
    ],
)
def test_bboxes_flip(axis, func, bboxes):
    bboxes = BBoxesInternalType(array=bboxes)
    assert np.array_equal(FGeometric.bboxes_flip(bboxes, axis).array, func(bboxes).array)


@pytest.mark.parametrize(
    "bboxes, params, expected",
    [
        (
            np.array([(0.5, 0.2, 0.9, 0.7)]),
            {"crop_coords": ((18, 18, 82, 82),), "crop_height": 64, "crop_width": 64, "rows": 100, "cols": 100},
            np.array([(0.5, 0.03125, 1.125, 0.8125)]),
        )
    ],
)
def test_crop_bboxes_by_coords(bboxes, params, expected):
    bboxes = BBoxesInternalType(array=bboxes)
    cropped_bboxes = A.crop_bboxes_by_coords(bboxes, **params)
    assert np.array_equal(cropped_bboxes.array, expected)


@pytest.mark.parametrize(
    "bboxes, params, expected",
    [
        (
            np.array([(0.5, 0.2, 0.9, 0.7)]),
            {"crop_height": 64, "crop_width": 64, "rows": 100, "cols": 100},
            np.array([(0.5, 0.03125, 1.125, 0.8125)]),
        )
    ],
)
def test_bboxes_center_crop(bboxes, params, expected):
    bboxes = BBoxesInternalType(array=bboxes)
    cropped_bboxes = A.bboxes_center_crop(bboxes, **params)
    assert np.array_equal(cropped_bboxes.array, expected)


@pytest.mark.parametrize(
    "bboxes, params, expected",
    [
        (
            np.array([(0.5, 0.2, 0.9, 0.7)]),
            {"x_min": 24, "y_min": 24, "x_max": 64, "y_max": 64, "rows": 100, "cols": 100},
            np.array([(0.65, -0.1, 1.65, 1.15)]),
        ),
        (
            np.array([(0.5, 0.2, 0.9, 0.7)]),
            {"x_min": 24, "y_min": 40, "x_max": 34, "y_max": 60, "rows": 100, "cols": 100},
            np.array([(1.3, -2.0, 3.3, 3.0)]),
        ),
    ],
)
def test_bboxes_crop(bboxes, params, expected):
    bboxes = BBoxesInternalType(array=bboxes)
    cropped_bboxes = A.bboxes_crop(bboxes, **params)
    assert np.array_equal(cropped_bboxes.array, expected)


@pytest.mark.parametrize(
    "bboxes, params, expected",
    [
        (
            np.array([(0.5, 0.2, 0.9, 0.7)]),
            {"crop_height": 80, "crop_width": 80, "h_start": 0.2, "w_start": 0.1, "rows": 100, "cols": 100},
            np.array([(0.6, 0.2, 1.1, 0.825)]),
        )
    ],
)
def test_bboxes_random_crop(bboxes, params, expected):
    bboxes = BBoxesInternalType(array=bboxes)
    cropped_bboxes = A.bboxes_random_crop(bboxes, **params)
    assert np.array_equal(cropped_bboxes.array, expected)


@pytest.mark.parametrize(
    "bboxes, factors, rows, cols, expect",
    [
        (
            np.array([(0.1, 0.2, 0.3, 0.4)]),
            0,
            100,
            200,
            np.array([(0.1, 0.2, 0.3, 0.4)]),
        ),
        (
            np.array([(0.1, 0.2, 0.3, 0.4)]),
            1,
            100,
            200,
            np.array([(0.2, 0.7, 0.4, 0.9)]),
        ),
        (
            np.array([(0.1, 0.2, 0.3, 0.4)]),
            2,
            100,
            200,
            np.array([(0.7, 0.6, 0.9, 0.8)]),
        ),
        (
            np.array([(0.1, 0.2, 0.3, 0.4)]),
            3,
            100,
            200,
            np.array([(0.6, 0.1, 0.8, 0.3)]),
        ),
    ],
)
def test_bboxes_rot90(bboxes, factors, rows, cols, expect):
    bboxes = BBoxesInternalType(array=bboxes)
    assert np.array_equal(FGeometric.bboxes_rot90(bboxes, factors, rows, cols).array, expect)


@pytest.mark.parametrize(
    "bboxes, axis, expect",
    [
        (
            np.array([(0.7, 0.1, 0.8, 0.4)]),
            0,
            np.array([(0.1, 0.7, 0.4, 0.8)]),
        ),
        (
            np.array([(0.7, 0.1, 0.8, 0.4)]),
            1,
            np.array([(0.6, 0.2, 0.9, 0.3)]),
        ),
    ],
)
def test_bboxes_transpose(bboxes, axis, expect):
    bboxes = BBoxesInternalType(bboxes)
    assert np.allclose(FGeometric.bboxes_transpose(bboxes, axis).array, expect)


@pytest.mark.parametrize(
    ["bboxes", "min_area", "min_visibility", "target"],
    [
        (
            [(0.1, 0.5, 1.1, 0.9), (-0.1, 0.5, 0.8, 0.9), (0.1, 0.5, 0.8, 0.9)],
            0,
            0,
            [(0.1, 0.5, 1.0, 0.9), (0.0, 0.5, 0.8, 0.9), (0.1, 0.5, 0.8, 0.9)],
        ),
        ([(0.1, 0.5, 0.8, 0.9), (0.4, 0.5, 0.5, 0.6)], 150, 0, [(0.1, 0.5, 0.8, 0.9)]),
        ([(0.1, 0.5, 0.8, 0.9), (0.4, 0.9, 0.5, 1.6)], 0, 0.75, [(0.1, 0.5, 0.8, 0.9)]),
        ([(0.1, 0.5, 0.8, 0.9), (0.4, 0.7, 0.5, 1.1)], 0, 0.7, [(0.1, 0.5, 0.8, 0.9), (0.4, 0.7, 0.5, 1.0)]),
    ],
)
def test_filter_bboxes(bboxes, min_area, min_visibility, target):
    filtered_bboxes = filter_bboxes(
        BBoxesInternalType(array=np.array(bboxes), targets=[()] * len(bboxes)),
        min_area=min_area,
        min_visibility=min_visibility,
        rows=100,
        cols=100,
    )
    assert np.array_equal(filtered_bboxes.array, np.array(target))


@pytest.mark.parametrize(
    ["bboxes", "img_width", "img_height", "min_width", "min_height", "target"],
    [
        [
            [(0.1, 0.1, 0.9, 0.9), (0.1, 0.1, 0.2, 0.9), (0.1, 0.1, 0.9, 0.2), (0.1, 0.1, 0.2, 0.2)],
            100,
            100,
            20,
            20,
            [(0.1, 0.1, 0.9, 0.9)],
        ],
        [
            [(0.1, 0.1, 0.9, 0.9), (0.1, 0.1, 0.2, 0.9), (0.1, 0.1, 0.9, 0.2), (0.1, 0.1, 0.2, 0.2)],
            100,
            100,
            20,
            0,
            [(0.1, 0.1, 0.9, 0.9), (0.1, 0.1, 0.9, 0.2)],
        ],
        [
            [(0.1, 0.1, 0.9, 0.9), (0.1, 0.1, 0.2, 0.9), (0.1, 0.1, 0.9, 0.2), (0.1, 0.1, 0.2, 0.2)],
            100,
            100,
            0,
            20,
            [(0.1, 0.1, 0.9, 0.9), (0.1, 0.1, 0.2, 0.9)],
        ],
    ],
)
def test_filter_bboxes_by_min_width_height(bboxes, img_width, img_height, min_width, min_height, target):
    filtered_bboxes = filter_bboxes(
        BBoxesInternalType(array=np.array(bboxes)),
        cols=img_width,
        rows=img_height,
        min_width=min_width,
        min_height=min_height,
    )
    assert np.array_equal(filtered_bboxes.array, np.array(target))


def test_fun_max_size():
    target_width = 256

    img = np.empty((330, 49), dtype=np.uint8)
    out = FGeometric.smallest_max_size(img, target_width, interpolation=cv2.INTER_LINEAR)

    assert out.shape == (1724, target_width)


def test_is_rgb_image():
    image = np.ones((5, 5, 3), dtype=np.uint8)
    assert F.is_rgb_image(image)

    multispectral_image = np.ones((5, 5, 4), dtype=np.uint8)
    assert not F.is_rgb_image(multispectral_image)

    gray_image = np.ones((5, 5), dtype=np.uint8)
    assert not F.is_rgb_image(gray_image)

    gray_image = np.ones((5, 5, 1), dtype=np.uint8)
    assert not F.is_rgb_image(gray_image)


def test_is_grayscale_image():
    image = np.ones((5, 5, 3), dtype=np.uint8)
    assert not F.is_grayscale_image(image)

    multispectral_image = np.ones((5, 5, 4), dtype=np.uint8)
    assert not F.is_grayscale_image(multispectral_image)

    gray_image = np.ones((5, 5), dtype=np.uint8)
    assert F.is_grayscale_image(gray_image)

    gray_image = np.ones((5, 5, 1), dtype=np.uint8)
    assert F.is_grayscale_image(gray_image)


def test_is_multispectral_image():
    image = np.ones((5, 5, 3), dtype=np.uint8)
    assert not is_multispectral_image(image)

    multispectral_image = np.ones((5, 5, 4), dtype=np.uint8)
    assert is_multispectral_image(multispectral_image)

    gray_image = np.ones((5, 5), dtype=np.uint8)
    assert not is_multispectral_image(gray_image)

    gray_image = np.ones((5, 5, 1), dtype=np.uint8)
    assert not is_multispectral_image(gray_image)


def test_brightness_contrast():
    dtype = np.uint8
    min_value = np.iinfo(dtype).min
    max_value = np.iinfo(dtype).max

    image_uint8 = np.random.randint(min_value, max_value, size=(5, 5, 3), dtype=dtype)

    assert np.array_equal(F.brightness_contrast_adjust(image_uint8), F._brightness_contrast_adjust_uint(image_uint8))

    assert np.array_equal(
        F._brightness_contrast_adjust_non_uint(image_uint8), F._brightness_contrast_adjust_uint(image_uint8)
    )

    dtype = np.uint16
    min_value = np.iinfo(dtype).min
    max_value = np.iinfo(dtype).max

    image_uint16 = np.random.randint(min_value, max_value, size=(5, 5, 3), dtype=dtype)

    assert np.array_equal(
        F.brightness_contrast_adjust(image_uint16), F._brightness_contrast_adjust_non_uint(image_uint16)
    )

    F.brightness_contrast_adjust(image_uint16)

    dtype = np.uint32
    min_value = np.iinfo(dtype).min
    max_value = np.iinfo(dtype).max

    image_uint32 = np.random.randint(min_value, max_value, size=(5, 5, 3), dtype=dtype)

    assert np.array_equal(
        F.brightness_contrast_adjust(image_uint32), F._brightness_contrast_adjust_non_uint(image_uint32)
    )

    image_float = np.random.random((5, 5, 3))

    assert np.array_equal(
        F.brightness_contrast_adjust(image_float), F._brightness_contrast_adjust_non_uint(image_float)
    )


def test_swap_tiles_on_image_with_empty_tiles():
    img = np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]], dtype=np.uint8)

    result_img = F.swap_tiles_on_image(img, [])

    assert np.array_equal(img, result_img)


def test_swap_tiles_on_image_with_non_empty_tiles():
    img = np.array([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3], [4, 4, 4, 4]], dtype=np.uint8)

    tiles = np.array([[0, 0, 2, 2, 2, 2], [2, 2, 0, 0, 2, 2]])

    target = np.array([[3, 3, 1, 1], [4, 4, 2, 2], [3, 3, 1, 1], [4, 4, 2, 2]], dtype=np.uint8)

    result_img = F.swap_tiles_on_image(img, tiles)

    assert np.array_equal(result_img, target)


@pytest.mark.parametrize("dtype", list(F.MAX_VALUES_BY_DTYPE.keys()))
def test_solarize(dtype):
    max_value = F.MAX_VALUES_BY_DTYPE[dtype]

    if dtype == np.dtype("float32"):
        img = np.arange(2**10, dtype=np.float32) / (2**10)
        img = img.reshape([2**5, 2**5])
    else:
        max_count = 1024
        count = min(max_value + 1, 1024)
        step = max(1, (max_value + 1) // max_count)
        shape = [int(np.sqrt(count))] * 2
        img = np.arange(0, max_value + 1, step, dtype=dtype).reshape(shape)

    for threshold in [0, max_value // 3, max_value // 3 * 2, max_value, max_value + 1]:
        check_img = img.copy()
        cond = check_img >= threshold
        check_img[cond] = max_value - check_img[cond]

        result_img = F.solarize(img, threshold=threshold)

        assert np.all(np.isclose(result_img, check_img))
        assert np.min(result_img) >= 0
        assert np.max(result_img) <= max_value


def test_posterize_checks():
    img = np.random.random([256, 256, 3])
    with pytest.raises(TypeError) as exc_info:
        F.posterize(img, 4)
    assert str(exc_info.value) == "Image must have uint8 channel type"

    img = np.random.randint(0, 256, [256, 256], dtype=np.uint8)
    with pytest.raises(TypeError) as exc_info:
        F.posterize(img, [1, 2, 3])
    assert str(exc_info.value) == "If bits is iterable image must be RGB"


def test_equalize_checks():
    img = np.random.randint(0, 255, [256, 256], dtype=np.uint8)

    with pytest.raises(ValueError) as exc_info:
        F.equalize(img, mode="other")
    assert str(exc_info.value) == "Unsupported equalization mode. Supports: ['cv', 'pil']. Got: other"

    mask = np.random.randint(0, 1, [256, 256, 3], dtype=bool)
    with pytest.raises(ValueError) as exc_info:
        F.equalize(img, mask=mask)
    assert str(exc_info.value) == "Wrong mask shape. Image shape: {}. Mask shape: {}".format(img.shape, mask.shape)

    img = np.random.randint(0, 255, [256, 256, 3], dtype=np.uint8)
    with pytest.raises(ValueError) as exc_info:
        F.equalize(img, mask=mask, by_channels=False)
    assert str(exc_info.value) == "When by_channels=False only 1-channel mask supports. " "Mask shape: {}".format(
        mask.shape
    )

    img = np.random.random([256, 256, 3])
    with pytest.raises(TypeError) as exc_info:
        F.equalize(img, mask=mask, by_channels=False)
    assert str(exc_info.value) == "Image must have uint8 channel type"


def test_equalize_grayscale():
    img = np.random.randint(0, 255, [256, 256], dtype=np.uint8)
    assert np.all(cv2.equalizeHist(img) == F.equalize(img, mode="cv"))


def test_equalize_rgb():
    img = np.random.randint(0, 255, [256, 256, 3], dtype=np.uint8)

    _img = img.copy()
    for i in range(3):
        _img[..., i] = cv2.equalizeHist(_img[..., i])
    assert np.all(_img == F.equalize(img, mode="cv"))

    _img = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
    img_cv = _img.copy()
    img_cv[..., 0] = cv2.equalizeHist(_img[..., 0])
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_YCrCb2RGB)
    assert np.all(img_cv == F.equalize(img, mode="cv", by_channels=False))


def test_equalize_grayscale_mask():
    img = np.random.randint(0, 255, [256, 256], dtype=np.uint8)

    mask = np.zeros([256, 256], dtype=bool)
    mask[:10, :10] = True

    assert np.all(cv2.equalizeHist(img[:10, :10]) == F.equalize(img, mask=mask, mode="cv")[:10, :10])


def test_equalize_rgb_mask():
    img = np.random.randint(0, 255, [256, 256, 3], dtype=np.uint8)

    mask = np.zeros([256, 256], dtype=bool)
    mask[:10, :10] = True

    _img = img.copy()[:10, :10]
    for i in range(3):
        _img[..., i] = cv2.equalizeHist(_img[..., i])
    assert np.all(_img == F.equalize(img, mask, mode="cv")[:10, :10])

    _img = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
    img_cv = _img.copy()[:10, :10]
    img_cv[..., 0] = cv2.equalizeHist(img_cv[..., 0])
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_YCrCb2RGB)
    assert np.all(img_cv == F.equalize(img, mask=mask, mode="cv", by_channels=False)[:10, :10])

    mask = np.zeros([256, 256, 3], dtype=bool)
    mask[:10, :10, 0] = True
    mask[10:20, 10:20, 1] = True
    mask[20:30, 20:30, 2] = True
    img_r = img.copy()[:10, :10, 0]
    img_g = img.copy()[10:20, 10:20, 1]
    img_b = img.copy()[20:30, 20:30, 2]

    img_r = cv2.equalizeHist(img_r)
    img_g = cv2.equalizeHist(img_g)
    img_b = cv2.equalizeHist(img_b)

    result_img = F.equalize(img, mask=mask, mode="cv")
    assert np.all(img_r == result_img[:10, :10, 0])
    assert np.all(img_g == result_img[10:20, 10:20, 1])
    assert np.all(img_b == result_img[20:30, 20:30, 2])


@pytest.mark.parametrize("dtype", ["float32", "uint8"])
def test_downscale_ones(dtype):
    img = np.ones((100, 100, 3), dtype=dtype)
    downscaled = F.downscale(img, scale=0.5)
    assert np.all(downscaled == img)


def test_downscale_random():
    img = np.random.rand(100, 100, 3)
    downscaled = F.downscale(img, scale=0.5)
    assert downscaled.shape == img.shape
    downscaled = F.downscale(img, scale=1)
    assert np.all(img == downscaled)


def test_maybe_process_in_chunks():
    image = np.random.randint(0, 256, (100, 100, 6), np.uint8)

    for i in range(1, image.shape[-1] + 1):
        before = image[:, :, :i]
        after = FGeometric.rotate(before, angle=1)
        assert before.shape == after.shape


def test_multiply_uint8_optimized():
    image = np.random.randint(0, 256, [256, 320], np.uint8)
    m = 1.5

    result = F._multiply_uint8_optimized(image, [m])
    tmp = F.clip(image * m, image.dtype, F.MAX_VALUES_BY_DTYPE[image.dtype])
    assert np.all(tmp == result)

    image = np.random.randint(0, 256, [256, 320, 3], np.uint8)
    result = F._multiply_uint8_optimized(image, [m])
    tmp = F.clip(image * m, image.dtype, F.MAX_VALUES_BY_DTYPE[image.dtype])
    assert np.all(tmp == result)

    m = np.array([1.5, 0.75, 1.1])
    image = np.random.randint(0, 256, [256, 320, 3], np.uint8)
    result = F._multiply_uint8_optimized(image, m)
    tmp = F.clip(image * m, image.dtype, F.MAX_VALUES_BY_DTYPE[image.dtype])
    assert np.all(tmp == result)


@pytest.mark.parametrize(
    "img", [np.random.randint(0, 256, [100, 100], dtype=np.uint8), np.random.random([100, 100]).astype(np.float32)]
)
def test_shift_hsv_gray(img):
    F.shift_hsv(img, 0.5, 0.5, 0.5)


def test_cv_dtype_from_np():
    assert get_opencv_dtype_from_numpy(np.uint8) == cv2.CV_8U
    assert get_opencv_dtype_from_numpy(np.uint16) == cv2.CV_16U
    assert get_opencv_dtype_from_numpy(np.float32) == cv2.CV_32F
    assert get_opencv_dtype_from_numpy(np.float64) == cv2.CV_64F
    assert get_opencv_dtype_from_numpy(np.int32) == cv2.CV_32S

    assert get_opencv_dtype_from_numpy(np.dtype("uint8")) == cv2.CV_8U
    assert get_opencv_dtype_from_numpy(np.dtype("uint16")) == cv2.CV_16U
    assert get_opencv_dtype_from_numpy(np.dtype("float32")) == cv2.CV_32F
    assert get_opencv_dtype_from_numpy(np.dtype("float64")) == cv2.CV_64F
    assert get_opencv_dtype_from_numpy(np.dtype("int32")) == cv2.CV_32S


@pytest.mark.parametrize(
    ["image", "mean", "std"],
    [
        [np.random.randint(0, 256, [100, 100, 3], dtype=np.uint8), [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]],
        [np.random.randint(0, 256, [100, 100, 3], dtype=np.uint8), 0.5, 0.5],
        [np.random.randint(0, 256, [100, 100], dtype=np.uint8), 0.5, 0.5],
    ],
)
def test_normalize_np_cv_equal(image, mean, std):
    mean = np.array(mean, dtype=np.float32)
    std = np.array(std, dtype=np.float32)

    res1 = F.normalize_cv2(image, mean, std)
    res2 = F.normalize_numpy(image, mean, std)
    assert np.allclose(res1, res2)


@pytest.mark.parametrize("beta_by_max", [True, False])
def test_brightness_contrast_adjust_equal(beta_by_max):
    image_int = np.random.randint(0, 256, [512, 512, 3], dtype=np.uint8)
    image_float = image_int.astype(np.float32) / 255

    alpha = 1.3
    beta = 0.14

    image_int = F.brightness_contrast_adjust(image_int, alpha, beta, beta_by_max)
    image_float = F.brightness_contrast_adjust(image_float, alpha, beta, beta_by_max)

    image_float = (image_float * 255).astype(int)

    assert np.abs(image_int.astype(int) - image_float).max() <= 1


def test_mosaic4():
    h = 10
    w = 20
    value = 5
    img1 = np.full((10, 10), 1)  # top left
    img2 = np.full((10, 10), 2)  # top right
    img3 = np.full((10, 10), 3)  # bottom left
    img4 = np.full((5, 5), 4)  # bottom right
    img_out = FGeometric.mosaic4([img1, img2, img3, img4], height=h, width=w, value=value)

    assert img_out.shape[:2] == (h, w)
    # top left
    assert np.all(img_out[:5, :10] == np.full((5, 10), 1))
    # top right
    assert np.all(img_out[:5, 10:] == np.full((5, 10), 2))
    # bottom left
    assert np.all(img_out[5:, :10] == np.full((5, 10), 3))
    # bottom right
    assert np.all(img_out[5:, 10:15] == np.full((5, 5), 4))
    # bottom right filled area
    assert np.all(img_out[5:, 15:] == np.full((5, 5), 5))


@pytest.mark.parametrize(
    ["bbox", "pos", "rows", "cols", "expected"],
    [
        ([0.5, 0.5, 0.6, 0.6], 0, 100, 100, [0.0, 0.0, 0.1, 0.1]),
        ([0.4, 0.5, 0.5, 0.6], 1, 100, 100, [0.9, 0.0, 1.0, 0.1]),
        ([0.0, 0.8, 0.2, 1.0], 2, 50, 50, [0.0, 0.9, 0.1, 1.0]),
        ([0.8, 0.8, 1.0, 1.0], 3, 50, 50, [0.9, 0.9, 1.0, 1.0]),
    ],
)
def test_bbox_mosaic4(bbox, pos, rows, cols, expected):
    h = 100
    w = 100
    actual = FGeometric.bbox_mosaic4(bbox, rows, cols, pos, h, w)
    assert np.array_equal(actual, expected)


@pytest.mark.parametrize(
    ["xy", "pos", "rows", "cols", "expected"],
    [
        ([50, 50], 0, 100, 100, [0, 0]),
        ([50, 50], 1, 100, 100, [100, 0]),
        ([0, 50], 2, 50, 50, [0, 100]),
        ([50, 50], 3, 50, 50, [100, 100]),
    ],
)
def test_keypoint_mosaic4(xy, pos, rows, cols, expected):
    h = 100
    w = 100
    keypoint = xy + [0, 0]  # (x, y, angle, scale)
    actual = FGeometric.keypoint_mosaic4(keypoint, rows, cols, pos, h, w)
    assert np.array_equal(actual[:2], expected)
