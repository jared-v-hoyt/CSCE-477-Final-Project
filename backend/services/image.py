import numpy as np
from PIL import Image


PIXEL_SIZE_BITS = 32
NUM_VALUES_PER_PIXEL = 4


def int_to_bits(integer):
    return ((integer.reshape(-1, 1) & (1 << np.arange(8))) != 0).astype(int)[:, ::-1]


def bits_to_int(bits):
    return (bits * (1 << np.arange(8)[::-1])).sum(axis=1)


def get_image_data(input_path):
    with Image.open(input_path) as image:
        bounding_box = (0, 0, image.width, image.height)
        crop_region = image.crop(bounding_box)
        data = np.array(crop_region.getdata(), dtype=np.uint8)
        data_bits = int_to_bits(data).reshape(-1)
    return data_bits


def put_image_data(input_path, output_path, encrypted_data):
    encrypted_data = encrypted_data.reshape(-1, PIXEL_SIZE_BITS)

    rgb_values = (
        bits_to_int(encrypted_data[:, :8]).astype(np.uint8),
        bits_to_int(encrypted_data[:, 8:16]).astype(np.uint8),
        bits_to_int(encrypted_data[:, 16:24]).astype(np.uint8),
        bits_to_int(encrypted_data[:, 24:]).astype(np.uint8)
    )

    encrypted_image = list(zip(*rgb_values))

    with Image.open(input_path) as image:
        bounding_box = (0, 0, image.width, image.height)
        crop_region = image.crop(bounding_box)
        crop_region.putdata(encrypted_image)
        image.paste(crop_region, bounding_box)
        image.save(output_path)
