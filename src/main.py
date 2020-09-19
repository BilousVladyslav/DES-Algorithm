from textwrap import wrap
import math, operator
from functools import reduce


def char_to_bin(char: str):
    return [int(bit) for bit in '{0:016b}'.format(ord(char[0]))]


def concatenate(args):
    return reduce(operator.iadd, args, [])


def string_to_data_block(string: str, b_size: int):
    data_blocks, d_block = [], []
    symbols_in_block = b_size / 16
    for index, symbol in enumerate(string):
        if index % symbols_in_block == 0:
            if index > 0:
                data_blocks.append(d_block)
            d_block = [0 for _ in range(b_size - 16)] + char_to_bin(symbol)
        else:
            start_pos = int(16 * (3 - index % symbols_in_block))
            d_block[start_pos: start_pos + 16] = char_to_bin(symbol)
    data_blocks.append(d_block)
    return data_blocks


def rotate_left(block, i):
    return block[i:] + block[:i]


def entropia(bin_num, round_num):
    count_z = str(bin_num).count('0')/len(bin_num)
    count_o = str(bin_num).count('1')/len(bin_num)
    res_z = count_z * math.log(count_z, 2) * (-1)
    res_o = count_o * math.log(count_o, 2) * (-1)
    print("Round {} Entropia = {} ".format(round_num, res_z + res_o))


class DES:
    KEY = '123atc5'

    IP_TABLE = [58,	50,	42,	34,	26,	18,	10,	2, 60,	52,	44,	36,	28,	20,	12,	4,
                62,	54,	46,	38,	30,	22,	14,	6, 64,	56,	48,	40,	32,	24,	16,	8,
                57,	49,	41,	33,	25,	17,	9, 1, 59,	51,	43,	35,	27,	19,	11,	3,
                61,	53,	45,	37,	29,	21,	13,	5,	63,	55,	47,	39,	31,	23,	15,	7]

    C0 = [57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18,
          10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36]

    D0 = [63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22,
          14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4]

    Ki = [
        13, 16, 10, 23, 0, 4,
        2, 27, 14, 5, 20, 9,
        22, 18, 11, 3, 25, 7,
        15, 6, 26, 19, 12, 1,
        40, 51, 30, 36, 46, 54,
        29, 39, 50, 44, 32, 47,
        43, 48, 38, 55, 33, 52,
        45, 41, 49, 35, 28, 31
    ]

    ROTATIONS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

    EXPANSION_TABLE = [
        31, 0, 1, 2, 3, 4,
        3, 4, 5, 6, 7, 8,
        7, 8, 9, 10, 11, 12,
        11, 12, 13, 14, 15, 16,
        15, 16, 17, 18, 19, 20,
        19, 20, 21, 22, 23, 24,
        23, 24, 25, 26, 27, 28,
        27, 28, 29, 30, 31, 0
    ]

    SBOX = [
        # S1
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7,
         0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
         4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0,
         15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],

        # S2
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10,
         3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
         0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15,
         13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],

        # S3
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8,
         13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
         13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7,
         1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],

        # S4
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15,
         13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
         10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4,
         3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],

        # S5
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9,
         14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
         4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14,
         11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],

        # S6
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11,
         10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
         9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6,
         4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],

        # S7
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1,
         13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
         1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2,
         6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],

        # S8
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7,
         1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
         7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8,
         2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ]

    P = [
        15, 6, 19, 20, 28, 11,
        27, 16, 0, 14, 22, 25,
        4, 17, 30, 9, 1, 7,
        23, 13, 31, 26, 2, 8,
        18, 12, 29, 5, 21, 10,
        3, 24
    ]

    FP = [
        39, 7, 47, 15, 55, 23, 63, 31,
        38, 6, 46, 14, 54, 22, 62, 30,
        37, 5, 45, 13, 53, 21, 61, 29,
        36, 4, 44, 12, 52, 20, 60, 28,
        35, 3, 43, 11, 51, 19, 59, 27,
        34, 2, 42, 10, 50, 18, 58, 26,
        33, 1, 41, 9, 49, 17, 57, 25,
        32, 0, 40, 8, 48, 16, 56, 24
    ]

    def key_as_byte(self):
        bytekey = ''
        for i in bytearray(self.KEY, encoding='ascii'):
            bytekey += '{0:08b}'.format(i)
        return bytekey

    def extend_key(self):
        bytekey = self.key_as_byte()
        extended_key = ''
        ones_count, i_pos = 0, 0

        for i in range(64):
            if (i+1) % 8 == 0:
                if ones_count % 2 != 0:
                    extended_key += '0'
                else:
                    extended_key += '1'
                ones_count = 0
            else:
                extended_key += bytekey[i_pos]
                ones_count += int(bytekey[i_pos])
                i_pos += 1
        return extended_key

    def generate_C0D0(self):
        key_block = self.extend_key()
        c0, d0 = '', ''
        for place in self.C0:
            c0 += key_block[place - 1]
        for place in self.D0:
            d0 += key_block[place - 1]
        return [c0, d0]

    def XOR(self, block_1, block_2):
        return ''.join([str(int(i) ^ int(j)) for i, j in zip(block_1, block_2)])

    def generate_key(self, vector, cycle: int):
        key = ''
        vect = rotate_left(vector[0] + vector[1], self.ROTATIONS[cycle-1])
        for place in self.Ki:
            key += vect[place]
        return key, [vect[:28], vect[28:]]

    def init_permutation(self, block):
        permutated_block = ''
        for place in self.IP_TABLE:
            permutated_block += block[place - 1]
        return permutated_block

    def feistel_function(self, vect, key):
        vector = ''
        for i in self.EXPANSION_TABLE:
            vector += str(vect[i])
        final = []
        for j, i in enumerate(wrap(self.XOR(vector, key), 6)):
            temp_box = [
                self.SBOX[int(j)][0:16],
                self.SBOX[int(j)][16:32],
                self.SBOX[int(j)][32:48],
                self.SBOX[int(j)][48:64]
            ]

            final.append(bin(temp_box[int(i[0] + i[-1], 2)]
                             [int(i[1:-1], 2)])[2:].zfill(4))
        result = ''
        final_block = ''.join(final)
        for i in self.P:
            result += str(final_block[i])
        return result

    def feistel_permutation(self, block, mode=0):
        data_block = ''
        for s in block:
            data_block += str(s)

        l_block, r_block = data_block[:32], data_block[32:]
        cd_vector = self.generate_C0D0()
        for j in range(1, 17):
            if mode == 1:
                j_key, cd_vector = self.generate_key(cd_vector, 17-j)
                l_block, r_block = r_block, l_block
            else:
                j_key, cd_vector = self.generate_key(cd_vector, j)
            r_block, l_block = self.XOR(self.feistel_function(r_block, j_key), l_block), r_block

            entropia(r_block + l_block, j)
        result, temp = '', r_block + l_block
        for i in self.FP:
            result += temp[i]
        return wrap(result, 8)


DES = DES()
def main(data, mod):
    if mod == 0:
        encrypted_list = []
        for mess in data:
            encrypted_list.append(''.join([hex(int(i, 2))[2:].zfill(
                2).upper() for i in DES.feistel_permutation(mess)]))

        print(''.join(encrypted_list))

    elif mod == 1:
        temp_li = []
        for mess in data:
            temp_li.append(''.join([hex(int(i, 2))[2:].zfill(
                        2).upper() for i in DES.feistel_permutation(mess, 1)]))
        print(temp_li)
        temp_str = [[chr(int(j, 16)) for j in wrap(i, 4) if int(j, 16) != 0] for i in temp_li]
        print(temp_str)


with open('input.txt', 'r', encoding='utf-8') as file:
    data = string_to_data_block(file.read(), 64)
    main(data, 1)

print(''.format(int('ffff', 16)))