import getpass
import os
import random
import sys
from datetime import datetime
from itertools import cycle
try:
    import numpy as np
    from PIL import Image
except ModuleNotFoundError:
    print('Enter the command: pip install numpy pillow')
    sys.exit()


class ImageCrypt():
    def __init__(self, password):
        self.password = password

    def encrypt(self, filename):
        new_filename = self.new_filename('e', filename)
        if new_filename is None:
            print(f'Error: file {new_filename} already exists')
        else:
            try:
                start = datetime.now()
                im = Image.open(filename)
                encrypted = self.get_pixels(im)
                numbers = self.password_to_numbers(self.password)
                for i in progress_bar(numbers, 'Encryption: '):
                    encrypted = self.rail_fence_encrypt(encrypted, i)
                self.create_and_save_image(encrypted, im.width, im.height, new_filename)
                print(f'Encrypted image saved as {new_filename}')
                print('Time:', datetime.now() - start)
            except FileNotFoundError as error:
                print(error)
                return

    def decrypt(self, filename):
        new_filename = self.new_filename('d', filename)
        if new_filename is None:
            print(f'Error: file {new_filename} already exists')
        else:
            try:
                start = datetime.now()
                im = Image.open(filename)
                decrypted = self.get_pixels(im)
                numbers = self.password_to_numbers(self.password[::-1])
                for i in progress_bar(numbers, 'Decryption: '):
                    decrypted = self.rail_fence_decrypt(decrypted, i)
                self.create_and_save_image(decrypted, im.width, im.height, new_filename)
                print(f'Decrypted image saved as {new_filename}')
                print('Time:', datetime.now() - start)
            except FileNotFoundError as error:
                print(error)
                return

    @staticmethod
    def get_pixels(im):
        print('Scanning...')
        colors = []
        for x in range(im.width):
            for y in range(im.height):
                color = im.getpixel((x, y))
                colors.append(color)
        return colors

    @staticmethod
    def password_to_numbers(password):
        numbers = [ord(i) for i in password]
        return numbers

    def rail_fence_encrypt(self, plaintext, rails):
        p = self.rail_pattern(rails)
        return sorted(plaintext, key=lambda i: next(p))

    def rail_fence_decrypt(self, ciphertext, rails):
        p = self.rail_pattern(rails)
        indexes = sorted(range(len(ciphertext)), key=lambda i: next(p))
        result = [''] * len(ciphertext)
        for i, c in zip(indexes, ciphertext):
            result[i] = c
        return result

    @staticmethod
    def rail_pattern(n):
        r = list(range(n))
        return cycle(r + r[-2:0:-1])

    @staticmethod
    def new_filename(mode, filename):
        new_filename = f'{filename[:len(filename) - 4]}-{mode}.png'
        if os.path.exists(new_filename):
            return None
        else:
            return new_filename

    @staticmethod
    def create_and_save_image(colors, width, height, filename):
        print('Creation...')
        im = Image.new('RGB', (width, height))
        image_array = np.array(im)
        i = 0
        for x in range(width):
            for y in range(height):
                r = colors[i][0]
                g = colors[i][1]
                b = colors[i][2]
                image_array[y][x] = (r, g, b)
                i += 1
        new_image = Image.fromarray(image_array, 'RGB')
        new_image.save(filename)


def progress_bar(it, prefix='', size=60, out=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'='*x}{('·'*(size-x))}]", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print('', flush=True, file=out)


def main():
    filename = input('Enter image filename: ')
    if filename[len(filename) - 3:] in ('png', 'jpg'):
        password = getpass.getpass(prompt='Enter password: ', stream=None)
        if len(password) >= 8:
            mode = input('Do you want to encrypt or decrypt the image [E/d]? ')
            if mode == 'd' or mode == 'D':
                ImageCrypt(password).decrypt(filename)
            else:
                ImageCrypt(password).encrypt(filename)
        else:
            print('Error: minimum password length: 8')
            return
    else:
        print('Error: only .png/.jpg format')
        return


if __name__ == '__main__':
    main()
