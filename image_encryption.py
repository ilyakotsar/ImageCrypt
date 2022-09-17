import os
import random
import sys
from datetime import datetime
from itertools import cycle
try:
    import numpy as np
    from PIL import Image
    from PIL import UnidentifiedImageError
except ModuleNotFoundError as error:
    print(error)
    print('Enter the command: pip install pillow numpy')
    sys.exit()


class ImageEncryption():
    def __init__(self, password):
        self.password = password

    def encrypt(self, filename):
        start = datetime.now()
        im = Image.open(filename)
        colors = self.get_pixels(im)
        numbers = self.password_to_integers(self.password)
        encrypted = colors
        for i in progress_bar(numbers, 'Encryption: '):
            encrypted = self.rail_fence_encrypt(encrypted, i)
        new_filename = self.new_filename('encrypted')
        self.create_and_save_image(encrypted, im.width, im.height, new_filename)
        print('Time:', datetime.now() - start)

    def decrypt(self, filename):
        start = datetime.now()
        im = Image.open(filename)
        colors = self.get_pixels(im)
        numbers = self.password_to_integers(self.password[::-1])
        decrypted = colors
        for i in progress_bar(numbers, 'Decryption: '):
            decrypted = self.rail_fence_decrypt(decrypted, i)
        new_filename = self.new_filename('decrypted', filename)
        if new_filename:
            self.create_and_save_image(decrypted, im.width, im.height, new_filename)
            print('Time:', datetime.now() - start)
        else:
            print('Error: the path is not empty')

    @staticmethod
    def get_pixels(im):
        print('')
        colors = []
        for x in progress_bar(range(im.width), 'Scanning: '):
            for y in range(im.height):
                color = im.getpixel((x, y))
                colors.append(color)
        return colors

    @staticmethod
    def password_to_integers(password):
        integers = [ord(i) for i in password]
        return integers

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
    def new_filename(mode, filename=None):
        while True:
            if filename is None:
                while True:
                    number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                    new_filename = f'{mode}_image_{number}.png'
                    if os.path.exists(new_filename):
                        continue
                    else:
                        break
                return new_filename
            else:
                number = filename.split('image_')[1].split('.')[0]
                new_filename = f'{mode}_image_{number}.png'
                if os.path.exists(new_filename):
                    return None
                else:
                    return new_filename

    @staticmethod
    def create_and_save_image(colors, width, height, filename):
        im = Image.new('RGB', (width, height))
        image_array = np.array(im)
        i = 0
        for x in progress_bar(range(width), 'Creation: '):
            for y in range(height):
                r = colors[i][0]
                g = colors[i][1]
                b = colors[i][2]
                image_array[y][x] = (r, g, b)
                i += 1
        new_image = Image.fromarray(image_array, 'RGB')
        new_image.save(filename)
        print(f'Image saved as {filename}')


def progress_bar(it, prefix='', size=60, out=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'='*x}{('·'*(size-x))}] {j}/{count}", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print('\n', flush=True, file=out)


def main():
    filename = input('Enter image filename: ')
    try:
        Image.open(filename)
    except (FileNotFoundError, UnidentifiedImageError) as error:
        print(error)
        return
    password = input('Enter password: ')
    if len(password) > 0:
        mode = input('Do you want to encrypt or decrypt the image [E/d]? ')
        if mode == 'e' or mode == 'E' or mode == '':
            ImageEncryption(password).encrypt(filename)
        elif mode == 'd' or mode == 'D':
            ImageEncryption(password).decrypt(filename)
        else:
            print('Error: invalid input')
        return
    else:
        print('Error: empty password')
        return


if __name__ == '__main__':
    main()
