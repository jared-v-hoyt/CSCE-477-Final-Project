import data.des_constants as constants
import numpy as np
from tqdm import tqdm


def permute(permutation_table, bit_string):
    return bit_string[permutation_table - 1]


class DES:
    def __init__(self, text):
        self.text = text
        self.key = self.Key()
        self.mode = self.Mode(self)

    class Key:
        def __init__(self):
            self.key = self.generate_key()
            self.subkeys = self.generate_subkeys()

        def generate_key(self):
            random_bit_generator = np.random.default_rng()
            random_bits = random_bit_generator.integers(low=0, high=2, size=64)
            return np.array(random_bits, dtype=np.uint8)

        def generate_subkeys(self):
            permuted_key = permute(constants.PC_1, self.key)

            c = permuted_key[:28]
            d = permuted_key[28:]

            subkeys = np.empty((16, 48), dtype=np.uint8)

            for i, shift in enumerate(constants.SHIFTS):
                c = np.roll(c, -1 * shift)
                d = np.roll(d, -1 * shift)

                cd_combined = np.hstack((c, d))

                subkey = permute(constants.PC_2, cd_combined)
                subkeys[i] = subkey

            return subkeys

    class Mode:
        def __init__(self, des: "DES"):
            self.des = des
            self.BLOCK_SIZE_BITS = 64
            self.SEGMENT_SIZE_BITS = 8
            self.padding = np.array([])

        def pad_text(self):
            # Padding will only (potentially) be set if the text is being decrypted.
            if  len(self.padding) > 0:
                self.des.text = np.concatenate((self.des.text, self.padding))
                return

            padding_length = len(self.des.text) % self.BLOCK_SIZE_BITS

            if padding_length:
                self.padding = np.zeros(self.BLOCK_SIZE_BITS - padding_length)
                self.des.text = np.concatenate((self.des.text, self.padding))

        def unpad_text(self):
            if len(self.padding) > 0:
                self.des.text = self.des.text[:len(self.des.text) - len(self.padding)]

        def ecb(self):
            num_blocks = len(self.des.text) // self.BLOCK_SIZE_BITS
            encryption = np.empty(num_blocks * self.BLOCK_SIZE_BITS, dtype=np.uint8)

            for i in tqdm(
                range(num_blocks),
                desc="Encryption in ECB Mode",
                total=num_blocks
            ):
                start = i * self.BLOCK_SIZE_BITS
                end = start + self.BLOCK_SIZE_BITS
                encrypted_block = self.des.encrypt(self.des.text[start:end])
                encryption[start:end] = encrypted_block

            return encryption

        def cbc(self):
            # TODO: create a more robust IV
            IV = np.zeros(self.BLOCK_SIZE_BITS, dtype=np.uint8)

            num_blocks = len(self.des.text) // self.BLOCK_SIZE_BITS
            encryption = np.empty(num_blocks * self.BLOCK_SIZE_BITS, dtype=np.uint8)

            for i in tqdm(
                range(num_blocks),
                desc="Encryption in CBC Mode",
                total=num_blocks
            ):
                start = i * self.BLOCK_SIZE_BITS
                end = start + self.BLOCK_SIZE_BITS

                block = np.bitwise_xor(self.des.text[start:end], IV)
                encrypted_block = self.des.encrypt(block)
                IV = encrypted_block
                encryption[start:end] = encrypted_block

            return encryption

        def cfb(self):
            shift_register = np.zeros(self.BLOCK_SIZE_BITS, dtype=np.uint8)

            num_segments = len(self.des.text) // self.SEGMENT_SIZE_BITS
            ciphertext = np.empty(num_segments * self.SEGMENT_SIZE_BITS, dtype=np.uint8)

            for i in tqdm(
                range(num_segments),
                desc="Encryption in CFB Mode",
                total=num_segments
            ):
                start = i * self.SEGMENT_SIZE_BITS
                end = start + self.SEGMENT_SIZE_BITS

                encryption = self.des.encrypt(shift_register)
                plaintext_segment = self.des.text[start:end]
                
                ciphertext_segment = np.bitwise_xor(encryption[:self.SEGMENT_SIZE_BITS], plaintext_segment)
                ciphertext[start:end] = ciphertext_segment

                shift_register = np.roll(shift_register, -self.SEGMENT_SIZE_BITS)
                shift_register[-self.SEGMENT_SIZE_BITS:] = ciphertext_segment

            return ciphertext

        def ofb(self):
            # TODO: create a more robust nonce
            nonce = np.zeros(self.BLOCK_SIZE_BITS, dtype=np.uint8)
            
            num_blocks = len(self.des.text) // self.BLOCK_SIZE_BITS
            plaintext = np.empty(num_blocks * self.BLOCK_SIZE_BITS, dtype=np.uint8)

            for i in tqdm(
                range(num_blocks),
                desc="Encryption in OFB Mode",
                total=num_blocks
            ):
                start = i * self.BLOCK_SIZE_BITS
                end = start + self.BLOCK_SIZE_BITS

                nonce = self.des.encrypt(nonce)
                plaintext_block = self.des.text[start:end]
                ciphertext_block = np.bitwise_xor(plaintext_block, nonce[:len(plaintext_block)])
                plaintext[start:end] = ciphertext_block

            return plaintext

        def ctr(self):
            num_blocks = len(self.des.text) // self.BLOCK_SIZE_BITS
            ciphertext = np.empty(num_blocks * self.BLOCK_SIZE_BITS, dtype=np.uint8)
            counter = 0
            bit_size = 64

            for i in tqdm(
                range(num_blocks),
                desc="Encryption in CTR Mode",
                total=num_blocks
            ):
                counter_block = np.array([(counter >> bit) & 1 for bit in range(bit_size - 1, -1, -1)], dtype=np.uint8)

                encryption = self.des.encrypt(counter_block)
                start = i * self.BLOCK_SIZE_BITS
                end = start + self.BLOCK_SIZE_BITS
                plaintext_block = self.des.text[start:end]
                ciphertext_block = np.bitwise_xor(plaintext_block, encryption[:len(plaintext_block)])
                ciphertext[start:end] = ciphertext_block

                counter = (counter + 1) % (2 ** bit_size)

            return ciphertext


    def encrypt(self, text):
        permuted_message = permute(constants.IP, text)
        l = permuted_message[:32]
        r = permuted_message[32:]

        for subkey in self.key.subkeys:
            xor = subkey ^ permute(constants.E_BIT, r)
            result = np.empty((0,), dtype=np.uint8)

            for i in range(8):
                six_bits = xor[i * 6 : (i + 1) * 6]
                row = (six_bits[0] << 1) + six_bits[5]
                col = (six_bits[1] << 3) + (six_bits[2] << 2) + (six_bits[3] << 1) + six_bits[4]

                s_box_value = constants.S_BOXES[i][row][col]
                result = np.concatenate((result, constants.S_BOX_CONVERSION[s_box_value]))

            f = permute(constants.P, result)
            l, r = r, l ^ f

        return permute(constants.IP_I, np.concatenate((r, l)))
